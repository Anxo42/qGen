import time
from typing import Optional
import PySide6
from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import *
from PySide6.QtGui import QIcon
import sys
import random
import Conection
import asyncio

class ConectionWindow(QWidget):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, parent=None):
        if not self.initialized:
            super().__init__(parent)
            self.initialized = True

            self.setFixedSize(800, 600)

            # Layout principal
            self.verticalLayout = QVBoxLayout(self)
            self.verticalLayout.setObjectName(u"verticalLayout")

            # Label 1
            self.label = QLabel(self)
            self.label.setObjectName(u"label")
            font = self.label.font()
            font.setFamilies([u"Times New Roman"])
            font.setPointSize(22)
            font.setBold(True)
            self.label.setFont(font)
            self.label.setAlignment(Qt.AlignCenter)
            self.label.setWordWrap(True)
            self.label.setText("qGen")

            self.verticalLayout.addWidget(self.label)

            # Label 2
            self.label_2 = QLabel(self)
            self.label_2.setObjectName(u"label_2")
            font1 = self.label_2.font()
            font1.setFamilies([u"Times New Roman"])
            font1.setPointSize(12)
            self.label_2.setFont(font1)
            self.label_2.setAlignment(Qt.AlignCenter)
            self.label_2.setText("Conections")

            self.verticalLayout.addWidget(self.label_2)

            # Lista
            self.list = QListWidget(self)
            self.list.setObjectName(u"list")

            self.verticalLayout.addWidget(self.list)

            # Widget con botones
            self.widget = QWidget(self)
            self.widget.setObjectName(u"widget")

            # Layout para los botones
            self.horizontalLayout = QHBoxLayout(self.widget)
            self.horizontalLayout.setObjectName(u"horizontalLayout")

            # Botón 1
            self.pushButton = QPushButton(self.widget)
            self.pushButton.setObjectName(u"pushButton")
            self.pushButton.setText("Start Search")
            #self.pushButton.clicked.connect(self.startConection)

            self.horizontalLayout.addWidget(self.pushButton)

            # Botón 2
            self.pushButton_2 = QPushButton(self.widget)
            self.pushButton_2.setObjectName(u"pushButton_2")
            self.pushButton_2.setText("Start Comunication")
            self.pushButton_2.setDisabled(1)

            # Selector de tiempo (QTimeEdit)
            self.timeEdit = QTimeEdit(self)
            self.timeEdit.setObjectName(u"timeEdit")
            self.timeEdit.setDisplayFormat("HH:mm:ss")
            #self.timeEdit.setTime(QTime(0, 0, 30))

            self.label = QLabel("Tiempo de la prueba", self)
            self.label.setObjectName(u"label")
            
            self.verticalLayout.addWidget(self.label)
            self.verticalLayout.addWidget(self.timeEdit)

            self.horizontalLayout.addWidget(self.pushButton_2)

            self.verticalLayout.addWidget(self.widget)

            self.setWindowIcon(QIcon('C:\\Users\\anxo4\\Documents\\tfgggggggg\\every-breath-you-take-master2\\every-breath-you-take-master\\logoQG.png'))
            self.setWindowTitle('qGen')


    async def startConection(self):
        self.list.insertItem(0, "Launching the scanner...")

        conection = Conection.Conection()      

        polar_device_found = False
        while not polar_device_found:
            devices = await conection.found_devices()
            await self.print_list(devices)
            polar_device = await conection.found_polar_device(devices)
            if polar_device is not None:
                polar_device_found = True
        await conection.connect_polar(polar_device)
        self.pushButton_2.setEnabled(1)

    
    async def print_list(self, devices):
        self.list.clear()
        print("Se muestran los dispositivos encontrados:")
        i = 0
        j = 0
        for device in devices:
            if device.name is None:
                device.name = "NoName" + str(j)
                j = j + 1
            print(f"{device.name}")
            self.list.insertItem(i, device.name)
            i = i + 1