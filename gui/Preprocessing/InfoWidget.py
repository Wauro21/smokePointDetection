import os
import sys
import cv2
import json
import datetime
from PyQt5.QtWidgets import QGroupBox, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5 import QtCore
from GUI_CONSTANTS import PREPROCESSING_AREA_INFORMATION_PARSER, PREPROCESSING_DISPLAY_CUT, PREPROCESSING_DISPLAY_CUT_WIDTH, PREPROCESSING_DISPLAY_DESC, PREPROCESSING_DISPLAY_INFO_HEIGHT, PREPROCESSING_DISPLAY_INFO_WIDTH, PREPROCESSING_DISPLAY_THRESHOLD, PREPROCESSING_DISPLAY_THRESHOLD_VALUE, PREPROCESSING_DISPLAY_TITLE, PREPROCESSING_DISPLAY_WIDTH_VALUE, PREPROCESSING_HEIGHT_INFORMATION_PARSER, PREPROCESSING_INFORMATION_TABLE_COLUMN_HEIGHT, PREPROCESSING_INFORMATION_TABLE_WIDTH, PREPROCESSING_TABLE_PADDING, PREPROCESSING_THESHOLD_CONTROLS_TITLE, PREPROCESSING_THRESHOLD_DESC, PREPROCESSING_THRESHOLD_FRAME_TITLE, PREPROCESSING_THRESHOLD_INFORMATION, PREPROCESSING_THRESHOLD_LOAD, PREPROCESSING_THRESHOLD_PERCENTAGE, PREPROCESSING_THRESHOLD_SAVE, PREPROCESSING_THRESHOLD_SPIN_WIDTH, PREPROCESSING_THRESHOLD_SUFFIX, PREPROCESSSING_ERROR_THRESHOLD_IMAGE, VIDEO_PLAYER_BG_COLOR
from CONSTANTS import MAX_PIXEL_VALUE, NUMBER_OF_CONNECTED_COMPONENTS
from MessageBox import ErrorBox, InformationBox
from Preprocessing.CommonButtons import LowerButtons
from utils import convert2QT, getConnectedComponents, getThreshvalues, resizeFrame
from PyQt5.QtCore import pyqtSignal, pyqtSlot



class DisplaySettings(QWidget):

    def __init__(self, process_controls, parent=None):
        super().__init__(parent)

        # Objects
        self.process_controls = process_controls

        # Widgets
        self.title = QLabel(PREPROCESSING_DISPLAY_TITLE, self)
        self.desc = QLabel(PREPROCESSING_DISPLAY_DESC, self)
        # -> Group box
        group = QGroupBox(self)
        self.cut_left = QLabel(group)
        self.cut_right = QLabel(group)
        self.cut_width = QLabel(group)
        self.core = QLabel(group)
        self.contour = QLabel(group)

        self.labels = [self.cut_left, self.cut_right, self.cut_width, self.core, self.contour]

        # -> Lower buttons
        self.apply = QPushButton('Apply')
        self.save = QPushButton('Save')
        

        # init routines

        self.initLabels()
        self.desc.setWordWrap(True)
        self.updateInfo()
        self.title.setStyleSheet(
            'font-weight: bold; font-size: 20px;'
        )
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        group.setFixedSize(PREPROCESSING_DISPLAY_INFO_WIDTH, PREPROCESSING_DISPLAY_INFO_HEIGHT)

        # Signals and Slots
        self.save.clicked.connect(self.save2JSON)

        # Layout
        layout = QVBoxLayout()

        # -> Group layout
        group_layout = QFormLayout()
        group_layout.addRow(PREPROCESSING_DISPLAY_CUT.format('left'), self.cut_left)
        group_layout.addRow(PREPROCESSING_DISPLAY_CUT.format('right'), self.cut_right)
        group_layout.addRow(PREPROCESSING_DISPLAY_CUT_WIDTH, self.cut_width)
        group_layout.addRow(PREPROCESSING_DISPLAY_THRESHOLD.format('Core'), self.core)
        group_layout.addRow(PREPROCESSING_DISPLAY_THRESHOLD.format('Contour'), self.contour)
        group.setLayout(group_layout)

        # -> Lower buttons
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.apply)
        buttons.addWidget(self.save)
        buttons.addStretch(1)

        layout.addWidget(self.title)
        layout.addWidget(self.desc)

        # -> Center info
        center = QHBoxLayout()
        center.addStretch(1)
        center.addWidget(group)
        center.addStretch(1)

        layout.addLayout(center)

        layout.addLayout(buttons)
        layout.addStretch(1)
        self.setLayout(layout)


    def applyHandler(self, function):
        self.apply.clicked.connect(function)

    def save2JSON(self):

        # Generate threshold dict
        save_dict = {
            'core_%': self.process_controls['core_%'],
            'contour_%': self.process_controls['contour_%'],
            'cut': self.process_controls['cut']
        }

        # Save file dialog
        date = datetime.datetime.now()
        date = date.strftime('%d-%m-%Y_%H-%M-%S')

        fileDialog = QFileDialog(self, windowTitle=PREPROCESSING_THRESHOLD_SAVE)
        save_file = fileDialog.getSaveFileName(
            self,
            PREPROCESSING_THRESHOLD_SAVE, 
            directory='run_config_{}.json'.format(date),
            filter='*.json',
        )

        if(save_file[0]):
            # Save the actual file
            with open(save_file[0], 'w') as file:
                json.dump(save_dict, file)

    def initLabels(self):

        for label in self.labels:
            label.setStyleSheet(
                'margin-left: 50px'
            )

    def updateInfo(self):

        # -> Check cut info
        cut_dict = self.process_controls['cut']
        if(cut_dict):
            self.cut_left.setText(str(cut_dict['left']))
            self.cut_right.setText(str(cut_dict['right']))
            width = str(cut_dict['right'] - cut_dict['left'])
            self.cut_width.setText(PREPROCESSING_DISPLAY_WIDTH_VALUE.format(width))

        else:
            self.cut_left.setText('-')
            self.cut_right.setText('-')
            self.cut_width.setText('-')

        # -> Set threshold values

        self.core.setText(PREPROCESSING_DISPLAY_THRESHOLD_VALUE.format(self.process_controls['core_%']))
        self.contour.setText(PREPROCESSING_DISPLAY_THRESHOLD_VALUE.format(self.process_controls['contour_%']))

        