from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QApplication
from PySide6.QtGui import QIcon
import sys

class ExportWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_directory_path = None

        self.setWindowTitle("Export Window")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout(self)

        self.select_directory_button = QPushButton("Select Directory", self)
        self.select_directory_button.clicked.connect(self.show_directory_dialog)

        self.directory_label = QLabel("Selected Directory: ", self)

        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)

        self.layout.addWidget(self.select_directory_button)
        self.layout.addWidget(self.directory_label)
        self.layout.addWidget(self.close_button)

        self.setWindowIcon(QIcon('C:\\Users\\anxo4\\Documents\\tfgggggggg\\every-breath-you-take-master2\\every-breath-you-take-master\\logoQG.png'))
        self.setWindowTitle('qGen')

    def show_directory_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        directory_dialog = QFileDialog()
        directory_dialog.setOptions(options)
        directory_dialog.setFileMode(QFileDialog.Directory)

        directory_path = directory_dialog.getExistingDirectory(self, "Select a Directory", "")

        if directory_path:
            self.selected_directory_path = directory_path
            self.directory_label.setText(f"Selected Directory: {directory_path}")

    def get_selected_directory_path(self):
        return self.selected_directory_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    export_window = ExportWindow()
    export_window.show()
    sys.exit(app.exec())
