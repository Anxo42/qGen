import asyncio
from PySide6.QtCore import QTimer, Qt, QPointF, QMargins, QSize, QFile
from PySide6.QtWidgets import *
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QScatterSeries, QSplineSeries, QAreaSeries
from PySide6.QtGui import QPen, QColor, QPainter, QFont
from bleak import BleakScanner
import time
import numpy as np
from Model import Model

class Conection:
    def __init__(self):
        self.model = Model()
        
    async def found_devices(self):
        print("Se ejecuta el escaner...")
        devices = await BleakScanner.discover()
        return devices

    async def found_polar_device(self, devices):
        polar_device_found = False
        polar_device = None
        print("Looking for Polar device...")
        print(f"Found {len(devices)} BLE devices")
        for device in devices:
            if device.name is not None and "Polar" in device.name:
                polar_device_found = True
                print(f"Found Polar device ")
                polar_device = device
                break
        if not polar_device_found:
            print("Polar device not found, retrying in 1 second")
            await asyncio.sleep(1)
        return polar_device
        
    async def connect_polar(self, device):
        self.model.set_polar_sensor(device)
        await self.model.connect_sensor()