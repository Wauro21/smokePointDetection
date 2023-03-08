import math
import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QFormLayout, QSpinBox, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QColor, QImage
from GUI_CONSTANTS import MOUSE_EVENT_PIXEL_OFFSET, PREPROCESSING_DESC_MESSAGE, PREPROCESSING_LOAD_CUT, PREPROCESSING_MINIMUM_WIDTH, PREPROCESSING_SAVE_CUT, PREPROCESSING_SCROLL_WIDTH_STEP, PREPROCESSING_TITLE_MESSAGE, PREPROCESSING_WINDOW_TITLE, VIDEO_PLAYER_BG_COLOR
from MessageBox import ErrorBox, InformationBox
from Preprocessing.CommonButtons import LowerButtons
from utils import convert2QT
from PyQt5.QtCore import pyqtSignal
import datetime
import json

class CutButtonsWidget(QWidget):
    cut_signal = pyqtSignal()
    update_frame = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        # Status 
        
        self.center_line_status = True
        self.width_status = True

        # Objects
        self.cut_dict = {
            'left': None,
            'right': None,
        }

        #Widgets
        self.title_label = QLabel(PREPROCESSING_TITLE_MESSAGE)
        self.desc_label = QLabel(PREPROCESSING_DESC_MESSAGE)
        self.center_line = QSpinBox(self)
        self.width = QSpinBox(self)
        self.lock_center_line = QPushButton('Lock')
        self.lock_width = QPushButton('Lock')
        self.auto = QPushButton('Auto')
        self.bottom_actions = LowerButtons(self)

        # Init routines
        self.title_label.setWordWrap(True)
        self.desc_label.setWordWrap(True)
        self.title_label.setStyleSheet('font-weight: bold')
        self.desc_label.setStyleSheet('margin-bottom: 25px')
        self.bottom_actions.setStyleSheet('margin-bottom: 100px')

        # Signals and Slots
        self.center_line.valueChanged.connect(lambda: self.update_frame.emit())
        self.width.valueChanged.connect(lambda: self.update_frame.emit())
        self.lock_center_line.clicked.connect(self.handleCenterLineControls)
        self.lock_width.clicked.connect(self.handleWidthControls)
        self.bottom_actions.apply.connect(lambda: self.cut_signal.emit())
        self.bottom_actions.save.connect(self.save2JSON)
        self.bottom_actions.load.connect(self.loadJSON)
        # Layout
        layout = QFormLayout()

        # -> Center line controls
        c_line_layout = QHBoxLayout()
        c_line_layout.addWidget(self.center_line)
        c_line_layout.addWidget(self.lock_center_line)

        # -> Width controls
        width_layout = QHBoxLayout()
        width_layout.addWidget(self.width)
        width_layout.addWidget(self.lock_width)        

        # -> General layout
        layout.addRow(self.title_label)
        layout.addRow(self.desc_label)
        layout.addRow('Center Line (x coordinate):', c_line_layout)
        layout.addRow('Width of Area of Interest:', width_layout)
        layout.addRow(self.auto)
        layout.addRow(self.bottom_actions)

        self.setLayout(layout)
        
    def autoHandler(self, function):
        self.auto.clicked.connect(function)
    
    def save2JSON(self):
        # Save file dialog
        date = datetime.datetime.now()
        date = date.strftime('%d-%m-%Y_%H-%M-%S')

        fileDialog = QFileDialog(self, windowTitle=PREPROCESSING_SAVE_CUT)
        save_file = fileDialog.getSaveFileName(
            self,
            PREPROCESSING_SAVE_CUT, 
            directory='cut_info_{}.json'.format(date),
            filter='*.json',
        )

        if(save_file[0]):
            # Save the actual file
            with open(save_file[0], 'w') as file:
                json.dump(self.cut_dict, file)

    def loadJSON(self):
        fileDialog = QFileDialog(self, windowTitle=PREPROCESSING_LOAD_CUT)
        fileDialog.setFileMode(QFileDialog.ExistingFile)
        fileDialog.setNameFilter('*.json')

        if fileDialog.exec_():
            file = fileDialog.selectedFiles()
            
            # Check if json is valid
            try:
                with open(file[0], 'r') as json_file:
                    json_dict = json.load(json_file)

                    try:
                        left = json_dict['left']
                        right = json_dict['right']

                    except:
                        message = ErrorBox('The provided JSON file is not in the correct format! Try with another file.')
                        message.exec_()
            except:
                message = ErrorBox('Not a valid JSON file.')
                message.exec_()

            # Succesfully loaded the dict
            width = right-left
            center = left + width//2

            self.updateCenterlinePos(center)
            self.updateWidth(width)

            # Inform user
            message = InformationBox('Presets loaded!')
            message.exec_()
            self.cut_signal.emit()

        

        


    def getCutDict(self):
        return self.cut_dict

    def setCutDict(self):
        center = self.center_line.value()
        width = self.width.value()

        self.cut_dict['left'] = center - (width//2)
        self.cut_dict['right'] = center + (width//2)

    

    def handleCenterLineControls(self):
        self.center_line_status = not self.center_line_status
        self.center_line.setEnabled(self.center_line_status)

    def handleWidthControls(self):
        self.width_status = not self.width_status
        self.width.setEnabled(self.width_status)

    def getCenterlinePos(self):
        return self.center_line.value()

    def getAreaWidth(self):
        return self.width.value()

    def initSpinsBoxes(self, min, max):
        self.initSpinBox(min, max, self.center_line)
        self.initSpinBox(PREPROCESSING_MINIMUM_WIDTH, max, self.width)

    def initSpinBox(self, min, max, box):
        box.setMinimum(min)
        box.setMaximum(max)
        
    def updateWidth(self, value):
        if(self.width.isEnabled()):
            self.width.setValue(value)
            self.setCutDict()

    def updateCenterlinePos(self, value):
        if(self.center_line.isEnabled()):
            self.center_line.setValue(value)
            self.setCutDict()

    def mouseIncrementWidth(self, step):
        if(self.width.isEnabled()):
            # get actual value from box
            a_width = self.width.value()
            # get max and min
            s_max = self.width.maximum()
            s_min = self.width.minimum()

            temp = a_width + step
            if(temp >= s_max):
                self.width.setValue(s_max)

            elif(temp <= s_min):
                self.width.setValue(s_min)

            else:
                self.width.setValue(temp)

        self.setCutDict()

