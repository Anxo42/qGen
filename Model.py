import numpy as np
import asyncio
from PolarH10 import PolarH10
import time
from scipy import signal
import BPMWindow

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressDialog, QProgressBar
from PySide6.QtCore import Qt, QThread, Signal, QTimer

class Model:
    _instance = None

    #Singleton
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Model, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.polar_sensor = None
        self.breathing_circle_radius = -0.5
        self.hr_circle_radius = -0.5

        # Sample rates
        self.ACC_UPDATE_LOOP_PERIOD = 0.01 # s, time to sleep between accelerometer updates
        self.IBI_UPDATE_LOOP_PERIOD = 0.01 # s, time to sleep between IBI updates
        self.ACC_HIST_SAMPLE_RATE = 20 # Hz, rate to subsample acceleration (raw data @ 200 Hz)
        self.BR_ACC_SAMPLE_RATE = 10 # Hz, rate to subsample breathing acceleration
        
        # History sizes
        self.BR_ACC_HIST_SIZE = 1200 # 
        self.IBI_HIST_SIZE = 400 # roughly number of seconds (assuming 60 bpm avg)
        self.HRV_HIST_SIZE = 500 
        self.BR_HIST_SIZE = 500 # Fast breathing 20 breaths per minute, sampled once every breathing cycle, over 10 minutes this is 200 values

        # Accelerometer signal parameters
        self.GRAVITY_ALPHA = 0.999 # Exponential mean filter for gravity
        self.ACC_MEAN_ALPHA = 0.98 # Exponential mean filter for noise
        self.acc_principle_axis = np.array([0, 0, 1]) # Positive z-axis is the direction out of sensor unit (away from chest)
        
        # Breathing signal parameters
        self.BR_MAX_FILTER = 30 # breaths per minute maximum

        # HRV signal parameters
        self.IBI_MIN_FILTER = 300 # ms
        self.IBI_MAX_FILTER = 1600 # ms
        self.HRV_MIN_FILTER = 0.2 # percentage allowable of last two HRV values

        # Initialisation
        self.acc_gravity = np.full(3, np.nan)
        self.acc_zero_centred_exp_mean = np.zeros(3)
        self.t_last_breath_acc_update = 0
        self.ibi_latest_phase_duration = 0
        self.ibi_last_phase = 0
        self.ibi_last_extreme = 0
        self.br_last_phase = 0
        self.current_br = 0

        # History array initialisation
        self.breath_acc_hist = np.full(self.BR_ACC_HIST_SIZE, np.nan)
        self.breath_acc_times = np.full(self.BR_ACC_HIST_SIZE, np.nan)
        self.breath_acc_times_rel_s = np.full(self.BR_ACC_HIST_SIZE, np.nan)

        self.br_psd_freqs_hist = []
        self.br_psd_values_hist = []
        
        self.ibi_values_hist = np.full(self.IBI_HIST_SIZE, np.nan)
        self.ibi_times_hist_rel_s = np.full(self.IBI_HIST_SIZE, np.nan) 
        self.ibi_values_interp_hist = [] # Interpolated IBI values
        self.ibi_times_interp_hist = [] # Interpolated IBI times
        self.ibi_values_last_cycle = [] # IBI values in the last breathing cycle
        self.hr_values_hist = np.full(self.IBI_HIST_SIZE, np.nan)
        
        self.hrv_values_hist = np.full(self.HRV_HIST_SIZE, np.nan) # HR range based on local IBI extrema
        self.hrv_times_hist = np.arange(-self.HRV_HIST_SIZE, 0) 

        self.hrv_psd_freqs_hist = []
        self.hrv_psd_values_hist = []

        self.hr_coherence = np.nan
        self.br_coherence = np.nan
        
        self.br_values_hist = np.full(self.BR_HIST_SIZE, np.nan)
        self.br_times_hist = np.full(self.BR_HIST_SIZE, np.nan) 
        self.br_times_hist_rel_s = np.full(self.BR_HIST_SIZE, np.nan) 
        
        self.rmssd_values_hist = np.full(self.BR_HIST_SIZE, np.nan)
        self.maxmin_values_hist = np.full(self.BR_HIST_SIZE, np.nan) # Max-min HR in a breathing cycle

        self.br_pace_values_hist = np.full(self.BR_HIST_SIZE, np.nan)

        self.hr_extrema_ids = np.full(self.HRV_HIST_SIZE, -1, dtype=int)
        self.breath_cycle_ids = np.full(self.BR_HIST_SIZE, -1, dtype=int)
        
    def set_polar_sensor(self, device):
        self.polar_sensor = PolarH10(device)

    async def connect_sensor(self):
        await self.polar_sensor.connect()
        await self.polar_sensor.get_device_info()
        await self.polar_sensor.print_device_info()
        
    async def disconnect_sensor(self):
        await self.polar_sensor.disconnect()

    
    async def update_ibi(self):
       
        await asyncio.sleep(self.IBI_UPDATE_LOOP_PERIOD)
        
        # Updating IBI history
        while not self.polar_sensor.ibi_queue_is_empty():
            t, ibi = self.polar_sensor.dequeue_ibi() # t is when value was added to the queue

            print(f"t:{t} ibi:{ibi}")
            
            # Skip unreasonably low or high values
            if ibi < self.IBI_MIN_FILTER or ibi > self.IBI_MAX_FILTER:
                continue

            # Update IBI and HR history
            self.ibi_values_hist = np.roll(self.ibi_values_hist, 1)
            self.ibi_values_hist[-1] = ibi
            self.hr_values_hist = 60.0/(self.ibi_values_hist/1000.0)
            print(f"{self.hr_values_hist[-1]}")


            self.ibi_times_hist_rel_s = np.roll(self.ibi_times_hist_rel_s, 1)
            self.ibi_times_hist_rel_s = -np.flip(np.cumsum(np.flip(self.ibi_values_hist)))/1000.0 # seconds relative to the last value

            
            self.ibi_times_hist_rel_s[0] = 0

            # self.ibi_times_hist_rel_s = np.flip(self.ibi_times_hist_rel_s)
            # self.ibi_values_hist = np.flip(self.ibi_values_hist)

            # self.ibi_values_hist = np.roll(self.ibi_values_hist, 1)
            # self.ibi_values_hist[1] = ibi
            # self.hr_values_hist = 60.0/(self.ibi_values_hist/1000.0)
            # print(f"{self.hr_values_hist[1]}")

            # self.ibi_times_hist_rel_s = -np.cumsum(self.ibi_values_hist)/1000.0 # seconds relative to the last value

            # self.ibi_times_hist_rel_s = np.roll(self.ibi_times_hist_rel_s, 1)
            # self.ibi_times_hist_rel_s[0] = 0
           

            # Update index of heart rate extrema
            self.hr_extrema_ids = self.hr_extrema_ids - 1
            self.hr_extrema_ids[self.hr_extrema_ids < -1] = -1

            bpm_value_new = 60.0/(ibi[-1]/1000.0)
            formatted_value = "{:.2f}".format(bpm_value_new)

            bpm_window = BPMWindow.BPMWindow()
            bpm_window.lcdNumber.display(formatted_value)


    def update_breathing_rate(self):

        # Update the breathing rate and pacer history
        if np.isnan(self.br_times_hist[-1]):
            self.br_values_hist = np.roll(self.br_values_hist, -1)
            self.br_values_hist[-1] = self.current_br

            self.br_pace_values_hist = np.roll(self.br_pace_values_hist, -1)
            self.br_pace_values_hist[-1] = 0

            self.br_times_hist = np.roll(self.br_times_hist, -1)
            self.br_times_hist[-1] = self.breath_acc_times[-1]

            self.rmssd_values_hist = np.roll(self.rmssd_values_hist, -1)
            self.rmssd_values_hist[-1] = 0

            self.maxmin_values_hist = np.roll(self.maxmin_values_hist, -1)
            self.maxmin_values_hist[-1] = 0
        else:

            # Update the breathing rate history
            self.br_values_hist = np.roll(self.br_values_hist, -1)
            self.br_values_hist[-1] = self.current_br

            self.br_pace_values_hist = np.roll(self.br_pace_values_hist, -1)
            self.br_pace_values_hist[-1] = self.pacer.last_breathing_rate  

            self.br_times_hist = np.roll(self.br_times_hist, -1)
            self.br_times_hist[-1] = self.breath_acc_times[-1]

            # Update the RMSSD history
            ibi_indices_in_cycle = self.ibi_times_hist_rel_s > (self.br_times_hist[-2] - time.time_ns()/1.0e9)
            self.ibi_values_last_cycle = self.ibi_values_hist[ibi_indices_in_cycle]
            ibi_ssd = self.ibi_values_hist[ibi_indices_in_cycle] - self.ibi_values_hist[np.roll(ibi_indices_in_cycle, -1)]
            rmssd = np.sqrt(np.mean(ibi_ssd**2))
            self.rmssd_values_hist = np.roll(self.rmssd_values_hist, -1)
            self.rmssd_values_hist[-1] = rmssd

            # Update the max-min history
            maxmin = np.max(self.ibi_values_hist[ibi_indices_in_cycle]) - np.min(self.ibi_values_hist[ibi_indices_in_cycle])
            self.maxmin_values_hist = np.roll(self.maxmin_values_hist, -1)
            self.maxmin_values_hist[-1] = maxmin

    def update_breathing_spectrum(self):
        if np.sum(~np.isnan(self.breath_acc_times)) < 3:
            return

        ids = self.breath_acc_times > (self.breath_acc_times[-1] - 30) # Hardcode 30 seconds
        values = self.breath_acc_hist[ids]
        times = self.breath_acc_times[ids]
        dt = times[-1] - times[-2]

        # Calculate the spectrum
        self.br_psd_freqs_hist, self.br_psd_values_hist = signal.periodogram(values, fs=1/dt, window='hann', detrend='linear')
        self.br_psd_values_hist /= np.sum(self.br_psd_values_hist)

        # Interpolating the power spectral density, to get sub-bin integration
        br_psd_freqs_interp = np.arange(self.br_psd_freqs_hist[0], self.br_psd_freqs_hist[-1], 0.005)
        br_psd_interp = np.interp(br_psd_freqs_interp, self.br_psd_freqs_hist, self.br_psd_values_hist)
        
        # Calculating total power and peak power
        pacer_freq = self.pacer.last_breathing_rate/60.0
        total_power = np.trapz(br_psd_interp, br_psd_freqs_interp)
        peak_indices = np.where((br_psd_freqs_interp >= pacer_freq - 0.015) & (br_psd_freqs_interp <= pacer_freq + 0.015)) # 0.03 Hz around the peak is recommended by R. McCraty
        peak_power = np.trapz(br_psd_interp[peak_indices], br_psd_freqs_interp[peak_indices])

        self.br_coherence = peak_power/total_power

    def update_acc_vectors(self, acc):
        # Update the gravity acc estimate (intialised to the first value)
        if np.isnan(self.acc_gravity).any():
            self.acc_gravity = acc
        else:
            self.acc_gravity = self.GRAVITY_ALPHA*self.acc_gravity + (1-self.GRAVITY_ALPHA)*acc

        # Unbias and denoise the acceleration
        acc_zero_centred = acc - self.acc_gravity
        self.acc_zero_centred_exp_mean = self.ACC_MEAN_ALPHA*self.acc_zero_centred_exp_mean + (1-self.ACC_MEAN_ALPHA)*acc_zero_centred

    def update_breathing_cycle(self):
        # Returns new_breathing_cycle

        self.breath_cycle_ids = self.breath_cycle_ids - 1
        self.breath_cycle_ids[self.breath_cycle_ids < -1] = -1

        current_br_phase = np.sign(self.breath_acc_hist[-1])

        # Exit if the phase hasn't changed or is non-negative
        if current_br_phase == self.br_last_phase or current_br_phase >= 0:
            self.br_last_phase = current_br_phase
            return 0

        # Calculate the breathing rate
        self.current_br = 60.0 / (self.breath_acc_times[-1] - self.br_times_hist[-1])
        
        # Filter out high breathing rates
        if self.current_br > self.BR_MAX_FILTER:
            return 0 

        # Save the index of the end of the cycle, the point of descending zero-crossing
        self.breath_cycle_ids = np.roll(self.breath_cycle_ids, -1)
        self.breath_cycle_ids[-1] = self.BR_ACC_HIST_SIZE - 1

        self.br_last_phase = current_br_phase

        if self.breath_cycle_ids[-2] < 0:
            return 0
        else: 
            return 1

    def update_breathing_acc(self, t):
        # Returns new_breathing_acc

        if t - self.t_last_breath_acc_update > 1/self.BR_ACC_SAMPLE_RATE:
            self.breath_acc_hist = np.roll(self.breath_acc_hist, -1)
            self.breath_acc_hist[-1] = np.dot(self.acc_zero_centred_exp_mean, self.acc_principle_axis)
            self.breath_acc_times = np.roll(self.breath_acc_times, -1)
            self.breath_acc_times[-1] = t
            self.t_last_breath_acc_update = t
            return 1
        else:  
            return 0

    def get_breath_circle_coords(self):
        
        if ~np.isnan(self.breath_acc_hist[-1]):
            self.breathing_circle_radius = 0.7*self.breath_acc_hist[-1] + (1-0.7)*self.breathing_circle_radius
        else: 
            self.breathing_circle_radius = -0.5
        self.breathing_circle_radius = np.min([np.max([self.breathing_circle_radius + 0.5, 0]), 1])

        x = self.breathing_circle_radius * self.pacer.cos_theta
        y = self.breathing_circle_radius * self.pacer.sin_theta
        return (x, y)

    async def update_acc(self): # pmd: polar measurement data
        
        await self.polar_sensor.start_acc_stream()
        
        while True:
            await asyncio.sleep(self.ACC_UPDATE_LOOP_PERIOD)
            
            # Updating the acceleration history
            while not self.polar_sensor.acc_queue_is_empty():
                # Get the latest sensor data
                t, acc = self.polar_sensor.dequeue_acc()

                # Update the acceleration vectors
                self.update_acc_vectors(acc)

                # Update breathing acceleration history
                new_breathing_acc = self.update_breathing_acc(t)

                # Update the breathing acceleration history
                if new_breathing_acc:
                    self.update_breathing_spectrum()
                    new_breathing_cycle = self.update_breathing_cycle()
                    
                    if new_breathing_cycle:
                        self.update_breathing_rate()


    