from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from PySide6.QtWidgets import *
import BPMWindow
import ConectionWindow
import asyncio
import sys
import Model
import statistics
import Acquisition
import DeviceInformationWindow
import Export
import ExportWindow
import openpyxl
from openpyxl.utils import get_column_letter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import ctypes
import os
import psutil
import time

class ViewManager(QWidget):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, parent=None):
        if not self.initialized:
            super().__init__(parent)

            self.model = Model.Model()
            self.conection_window = ConectionWindow.ConectionWindow()
            self.acquisition = Acquisition.Acquisition()
            self.bpm_window = BPMWindow.BPMWindow()
            self.deviceinformation_window = DeviceInformationWindow.DeviceInformationWindow()
            self.export_window = ExportWindow.ExportWindow()

            self.initialized = True

            self.successful_acquisition = False

            self.conection_window.pushButton.clicked.connect(lambda: asyncio.ensure_future(self.startConection()))
            self.conection_window.pushButton_2.clicked.connect(lambda: asyncio.ensure_future(self.after_conection()))

    async def after_conection(self):
        self.conection_window.hide()
        self.bpm_window.show()
        await main.bpm_window.start_acquisition()
    
    async def startConection(self):
        await self.conection_window.startConection()

    def calcular_estadisticas(self,hr_values):
    # Calcular estadísticas
        minimo = min(hr_values)
        maximo = max(hr_values)
        media = statistics.mean(hr_values)
        varianza = statistics.variance(hr_values)
        desviacion_tipica = statistics.stdev(hr_values)

        print(f'Mínimo: {minimo}')
        print(f'Máximo: {maximo}')
        print(f'Media: {media}')
        print(f'Varianza: {varianza}')
        print(f'Desviación Típica: {desviacion_tipica}')

        return minimo, maximo, media, varianza, desviacion_tipica

    def merge_arrays(self, array1, array2):
    # Verificar que ambos arrays tengan la misma longitud
        if len(array1) != len(array2):
            raise ValueError("Los arrays deben tener la misma longitud para realizar el merge.")

        # Inicializar el array resultante
        merged_array = []

        # Combinar elementos de ambos arrays con una coma entre ellos
        for elemento1, elemento2 in zip(array1, array2):
            merged_element = f"{elemento1},{elemento2}"
            merged_array.append(merged_element)

        return merged_array
    
    def filtrar_nan(self,arr):
        # Utiliza la función isnan de numpy para obtener una máscara booleana de valores no NaN
        mascara_no_nan = ~np.isnan(arr)
        
        # Filtra el array utilizando la máscara
        arr_filtrado = arr[mascara_no_nan]
        
        return arr_filtrado
        
    def export_report(self,path):
        # Filtrar y calcular estadísticas
        filtered_array = self.filtrar_nan(self.model.hr_values_hist)
        minimo, maximo, media, varianza, des_tipica = self.calcular_estadisticas(filtered_array)

        excel_filename = 'resultados_estadisticas.xlsx'
        excel_filename = path

        # Crear instancia de Export y generar el informe
        export = Export.Export(excel_filename, filtered_array, minimo, maximo, media, varianza, des_tipica)
        export.generate_report()

try:
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    main = ViewManager()
    main.conection_window.show()
    

    loop.run_forever()

    if main.bpm_window.acquisition_status == True:
        main.export_window.show()
        loop.run_forever()
        main.export_report(main.export_window.get_selected_directory_path())
        ctypes.windll.user32.MessageBoxW(0, f"El reporte se ha guardado correctamente.", "File Saved!", 0x40)

    else:
        ctypes.windll.user32.MessageBoxW(0, f"Se produjo un error en la adquisición de los datos.", "Error", 0x10)


except Exception as e:
    ctypes.windll.user32.MessageBoxW(0, f"Se produjo una excepción: {str(e)}", "Error", 0x10)
    sys.exit(1)