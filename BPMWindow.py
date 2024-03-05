import asyncio
from typing import Optional
from PySide6.QtCore import QTimer, Qt, QPointF, QMargins, QSize, QFile
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QScatterSeries, QSplineSeries, QAreaSeries
from PySide6.QtGui import QPen, QColor, QPainter, QFont, QIcon
from PySide6.QtWidgets import QWidget, QListWidget, QLCDNumber, QGridLayout
from bleak import BleakScanner
import time
import numpy as np
import Acquisition
import PolarH10
import Model


class BPMWindow(QWidget):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
            cls._instance.acquisition_status = False
        return cls._instance

    def __init__(self, parent=None):
        if not self.initialized:
            super().__init__(parent)

            self.model = Model.Model()

            self.setFixedSize(799, 600)

            self.gridLayout = QGridLayout(self)
            self.gridLayout.setObjectName(u"gridLayout")

            self.label = QLabel(self)
            self.label.setObjectName(u"label")
            font = self.label.font()
            font.setFamilies([u"Source Serif Pro Black"])
            font.setPointSize(72)
            font.setBold(True)
            self.label.setFont(font)
            self.label.setAlignment(Qt.AlignCenter)
            self.label.setText("BPM")

            self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

            self.lcdNumber = QLCDNumber(self)
            self.lcdNumber.setObjectName(u"lcdNumber")
            self.lcdNumber.setSmallDecimalPoint(True)

            self.gridLayout.addWidget(self.lcdNumber, 1, 0, 1, 1)

            self.initialized = True

            self.setWindowIcon(QIcon('C:\\Users\\anxo4\\Documents\\tfgggggggg\\every-breath-you-take-master2\\every-breath-you-take-master\\logoQG.png'))
            self.setWindowTitle('qGen')

    def set_polar_sensor(self, device):
        self.polar_sensor = PolarH10.PolarH10(device)
        self.acquisition.set_polar_sensor(device)

    async def start_acquisition(self):
        acquisition = Acquisition.Acquisition()
        self.acquisition_status = await acquisition.start_acquisition()

    



