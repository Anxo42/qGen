from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QProgressBar, QPushButton, QWidget)
from PySide6.QtGui import QIcon

class DeviceInformationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(435, 386)

        # Layout principal
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")

        # Label 1
        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.verticalLayout.addWidget(self.label)

        # Label Model Number
        self.label_modelnumber = QLabel(self)
        self.label_modelnumber.setObjectName(u"label_modelnumber")
        self.verticalLayout.addWidget(self.label_modelnumber)

        # Label 2
        self.label_3 = QLabel(self)
        self.label_3.setObjectName(u"label_3")
        self.verticalLayout.addWidget(self.label_3)

        # Label Manufacturer Name
        self.label_manufacturerName = QLabel(self)
        self.label_manufacturerName.setObjectName(u"label_manufacturerName")
        self.verticalLayout.addWidget(self.label_manufacturerName)

        # Label 3
        self.label_5 = QLabel(self)
        self.label_5.setObjectName(u"label_5")
        self.verticalLayout.addWidget(self.label_5)

        # Label Serial Number
        self.label_serialnumber = QLabel(self)
        self.label_serialnumber.setObjectName(u"label_serialnumber")
        self.verticalLayout.addWidget(self.label_serialnumber)

        # Label 4
        self.label_7 = QLabel(self)
        self.label_7.setObjectName(u"label_7")
        self.verticalLayout.addWidget(self.label_7)

        # Label Address
        self.label_address = QLabel(self)
        self.label_address.setObjectName(u"label_address")
        self.verticalLayout.addWidget(self.label_address)

        # Label Battery Level
        self.label_betterylevel = QLabel(self)
        self.progressBar = QProgressBar(self)
        self.verticalLayout.addWidget(self.label_betterylevel)
        self.verticalLayout.addWidget(self.progressBar)

        # Label 5
        self.label_2 = QLabel(self)
        self.label_2.setObjectName(u"label_2")
        self.verticalLayout.addWidget(self.label_2)

        # Label Firmware Revision
        self.label_firmwarerevision = QLabel(self)
        self.label_firmwarerevision.setObjectName(u"label_firmwarerevision")
        self.verticalLayout.addWidget(self.label_firmwarerevision)

        # Label 6
        self.label_15 = QLabel(self)
        self.label_15.setObjectName(u"label_15")
        self.verticalLayout.addWidget(self.label_15)

        # Label Hardware Revision
        self.label_hardwarerevision = QLabel(self)
        self.label_hardwarerevision.setObjectName(u"label_hardwarerevision")
        self.verticalLayout.addWidget(self.label_hardwarerevision)

        # Label 7
        self.label_11 = QLabel(self)
        self.label_11.setObjectName(u"label_11")
        self.verticalLayout.addWidget(self.label_11)

        # Label Software Revision
        self.label_softwarerevision = QLabel(self)
        self.label_softwarerevision.setObjectName(u"label_softwarerevision")
        self.verticalLayout.addWidget(self.label_softwarerevision)

        self.setWindowIcon(QIcon('C:\\Users\\anxo4\\Documents\\tfgggggggg\\every-breath-you-take-master2\\every-breath-you-take-master\\logoQG.png'))
        self.setWindowTitle('Polar H10')

        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Device Information")
        self.label.setText("Model Number:")
        self.label_modelnumber.setText("TextLabel")
        self.label_3.setText("Manufacturer Name:")
        self.label_manufacturerName.setText("TextLabel")
        self.label_5.setText("Serial Number:")
        self.label_serialnumber.setText("TextLabel")
        self.label_7.setText("Address:")
        self.label_address.setText("TextLabel")
        self.label_betterylevel.setText("Battery Level:")
        self.label_2.setText("Firmware Revision:")
        self.label_firmwarerevision.setText("TextLabel")
        self.label_15.setText("Hardware Revision:")
        self.label_hardwarerevision.setText("TextLabel")
        self.label_11.setText("Software Revision:")
        self.label_softwarerevision.setText("TextLabel")