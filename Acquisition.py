import asyncio
import signal
from PySide6.QtCore import QTimer, Qt, QPointF, QMargins, QSize, QFile, SignalInstance, Signal, QObject
from PySide6.QtWidgets import *
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QScatterSeries, QSplineSeries, QAreaSeries
from PySide6.QtGui import QPen, QColor, QPainter, QFont
from bleak import BleakScanner
import time
import numpy as np
import PolarH10
from BPMWindow import *
import Model
import ConectionWindow
import threading


class Acquisition:

    _instance = None
    new_hr_value = Signal(float)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Acquisition, cls).__new__(cls)
            cls._instance.model = Model.Model()
            cls._instance.conection_window = ConectionWindow.ConectionWindow()
            cls._instance.new_hr_value = SignalInstance(object)
            cls._instance.IBI_UPDATE_LOOP_PERIOD = 0.01
        return cls._instance
    
    async def start_acquisition(self):
        duration_qtime = self.conection_window.timeEdit.time()


        duration = duration_qtime.hour() * 3600 + duration_qtime.minute() * 60 + duration_qtime.second()

        print(f"Start Acquisition for {duration} seconds...")

        end_time = asyncio.get_event_loop().time() + duration
        polar_sensor = PolarH10.PolarH10(self.model.polar_sensor)
        await polar_sensor.start_hr_stream()

        while asyncio.get_event_loop().time() < end_time:
            hr_value = await self.model.update_ibi()
            print(f"{asyncio.get_event_loop().time()}/{end_time}")

        print("Acquisition finished.")

        # Mostrar el cuadro de diálogo después de que la adquisición haya terminado
        if asyncio.get_event_loop().time() >= end_time:
            return True
        else:
            return False

    def update_series(self):
        print("update series en acquisition")
        flag = True
        #self.br_times_hist_rel_s = self.model.br_times_hist - time.time_ns()/1.0e9

        series_hr_new = []
        i, value = self.model.hr_values_hist
        return value
        