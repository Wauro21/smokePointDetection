import sys
import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QLineEdit, QPushButton, QFileDialog

from GUI_CONSTANTS import LOAD_WIDGET_FILE_DEFAULT_MESSAGE, LOAD_WIDGET_FILE_DIALOG_HEADER_TITLE
from MessageBox import WarningBox
from Preprocessing.CutWidget import CutWidget
from Preprocessing.Preprocessing import PreprocessingWidget
from Preprocessing.ThresholdWidget import ThresholdWidget
__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'


class LoadWidget(QWidget):

    # Custom signals
    path_signal = QtCore.pyqtSignal(list)
    cut_info = QtCore.pyqtSignal()

    def __init__(self, process_controls,  parent=None):
        super().__init__(parent)
        
        # Objects 
        self.processControls = process_controls

        # Widgets 

        self.field_description = QLabel('File:')
        self.display_path = QLineEdit(LOAD_WIDGET_FILE_DEFAULT_MESSAGE, self)
        self.open_button = QPushButton('Open')

        # -> Configure run button
        self.configure_button = QPushButton('Configure run')
        
        #  Init routine
        self.configure_button.setEnabled(False)

        # -> Bold texts for labels
        self.field_description.setStyleSheet(
            "font-weight: bold;"
        )

        # -> QLineEdit size 
        self.display_path.setStyleSheet(
            "width : 500; margin-left : 10px;"
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
        layout.addWidget(self.configure_button)

        self.setLayout(layout)

    def getDemoFrame(self):
        return self.demo_frame

    def configureHandler(self, function):
        self.configure_button.clicked.connect(function)

    def getFiles(self):
        valid = False
        while not valid:
            fileDialog = QFileDialog(self, windowTitle=LOAD_WIDGET_FILE_DIALOG_HEADER_TITLE)
            # This is a limitation of the pyqt framework, only files OR folders can be configured to be selected
            # by the native OS dialog. A workaround exists but doesnt look good as it doesn't uses the native dialog.
            fileDialog.setFileMode(QFileDialog.Directory)

            if fileDialog.exec_():
                folder = fileDialog.selectedFiles()[0]
                # Validate folder
                valid = self.checkFolder(folder)


                self.setDisplayLabel(folder)
                
                # Enable preprocessing 
                self.configure_button.setEnabled(True)
            else:
                # User pressed cancel
                break

    def setDisplayLabel(self, folder):
        self.display_path.setText(folder)

    def checkFolder(self, folder):

        if not (os.path.isdir(folder)):
            warning = WarningBox('Selected option is not a folder!', self)
            warning.exec_()
            return False

        # List files
        files = os.listdir(folder)
        files.sort()
        prefix = files[0].replace('0000', '%04d')

        if(files[0] == prefix):
            # Something didn't work on the prefix, probably some weird files
            warning = WarningBox('Frames inside the folder are not numerated in order starting from 0000.')
            warning.exec_()
            return False
        
        # Save first frame location for preprocessing
        demo_frame = os.path.join(folder, files[0])

        frames_path = os.path.join(folder, prefix)
        self.path_signal.emit([frames_path, demo_frame])        
        return True

if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')

    widget = LoadWidget()
    widget.show()
    sys.exit(app.exec_())