import sys
import os
import json
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QLineEdit, QPushButton, QFileDialog
from PySide2.QtCore import Signal

from gui.GUI_CONSTANTS import LOAD_START_BUTTON_ENABLED_TEXT, LOAD_START_BUTTON_STOP_TEXT, LOAD_WIDGET_FILE_DEFAULT_MESSAGE, LOAD_WIDGET_FILE_DIALOG_HEADER_TITLE, LOAD_WIDGET_LOAD_JSON, StartStates
from gui.MessageBox import ErrorBox, LoadBox, WarningBox
__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'


class LoadWidget(QWidget):

    # Custom signals
    start = Signal()
    stop = Signal()
    path_signal = Signal(list)
    cut_info = Signal()
    load_config = Signal()

    def __init__(self, process_controls,  parent=None):
        super().__init__(parent)
        
        # Objects 
        self.process_controls = process_controls
        self.start_btn_state = StartStates.LOCKED

        # Widgets 

        self.field_description = QLabel('File:')
        self.display_path = QLineEdit(LOAD_WIDGET_FILE_DEFAULT_MESSAGE, self)
        self.open_button = QPushButton('Open')

        # -> Configure run button
        self.configure_button = QPushButton('Configure run')
        self.load_presets = QPushButton('Load settings')

        # -> Start button
        self.start_button = QPushButton(LOAD_START_BUTTON_ENABLED_TEXT, self)
        
        #  Init routine
        self.handleStartButton()

        self.configure_button.setEnabled(False)
        self.load_presets.setEnabled(False)

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
        self.load_presets.clicked.connect(self.loadJSON)
        self.start_button.clicked.connect(self.startButtonSignalHandler)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.field_description)
        layout.addWidget(self.display_path)
        layout.addWidget(self.open_button)
        layout.addWidget(self.configure_button)
        layout.addWidget(self.load_presets)
        layout.addWidget(self.start_button)

        self.setLayout(layout)


    def lockUserControls(self, lock):
        self.open_button.setEnabled(lock)
        self.configure_button.setEnabled(lock)
        self.load_presets.setEnabled(lock)


    def startButtonSignalHandler(self):        
        if(self.start_btn_state is StartStates.ENABLED):
            self.start.emit()

        elif(self.start_btn_state is StartStates.STOP):
            self.stop.emit()

    def externalStartButton(self, state):
        self.start_btn_state = state
        self.handleStartButton()


    def handleStartButton(self):

        # Restore color
        self.start_button.setStyleSheet(
            'background-color: #3ede49'
        )

        if(self.start_btn_state is StartStates.LOCKED):
            # Disable button
            self.start_button.setEnabled(False)
            

        elif(self.start_btn_state is StartStates.ENABLED):
            # Enable button
            self.start_button.setEnabled(True)

            # Display text 
            self.start_button.setText(LOAD_START_BUTTON_ENABLED_TEXT)

        elif(self.start_btn_state is StartStates.STOP):

            # Display text
            self.start_button.setText(LOAD_START_BUTTON_STOP_TEXT)

            # Change color 
            self.start_button.setStyleSheet(
            'background-color: #FF4242'
            )
            



    def loadJSON(self):
            fileDialog = QFileDialog(self, windowTitle=LOAD_WIDGET_LOAD_JSON)
            fileDialog.setFileMode(QFileDialog.ExistingFile)
            fileDialog.setNameFilter('*.json')

            if fileDialog.exec_():
                file = fileDialog.selectedFiles()
                
                # Check if json is valid
                with open(file[0], 'r') as json_file:
                    json_dict = json.load(json_file)

                    try:
                        
                        for key in self.process_controls['controls']:
                            self.process_controls['controls'][key] = json_dict[key]

                        self.externalStartButton(StartStates.ENABLED)
                        
                        # Inform user
                        self.load_config.emit()
                        message = LoadBox(self.process_controls)
                        message.exec_()

                    except:
                        message = ErrorBox('The provided JSON file is not in the correct format! Try with another file.')
                        message.exec_()
                

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
                self.load_presets.setEnabled(True)
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

        # Save number of frames
        self.process_controls['frames_info']['n_frames'] = len(files)

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