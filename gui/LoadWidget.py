import sys
import os

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QLineEdit, QPushButton, QFileDialog

from Constants import LOAD_WIDGET_FILE_DEFAULT_MESSAGE

__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'


class LoadWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Objects 


        # Widgets 

        self.field_description = QLabel('File:')
        self.display_path = QLineEdit(LOAD_WIDGET_FILE_DEFAULT_MESSAGE, self)
        self.open_button = QPushButton('Open')

        #  Init routine
        # -> Bold texts for labels
        self.field_description.setStyleSheet(
            "font-weight: bold;"
        )

        # -> QLineEdit size 
        self.display_path.setStyleSheet(
            "width : 500px; margin-left : 10px;"
        )

        # -> QLineEdit to display the path or file being selected
        self.display_path.setReadOnly(True)

        # Signals and slots
        self.open_button.clicked.connect(self.getFiles)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.field_description)
        layout.addWidget(self.display_path)
        layout.addWidget(self.open_button)

        self.setLayout(layout)

    def getFiles(self):
        fileDialog = QFileDialog()
        
        if fileDialog.exec_():
            filenames = fileDialog.selectedFiles()
            print(filenames)



if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')

    widget = LoadWidget()
    widget.show()
    sys.exit(app.exec_())