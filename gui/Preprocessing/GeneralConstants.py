import os
import sys
import cv2
import json
import datetime
from PyQt5.QtWidgets import QGroupBox, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QDoubleSpinBox
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5 import QtCore
from GUI_CONSTANTS import PREPROCESSING_AREA_INFORMATION_PARSER, PREPROCESSING_CONSTANTS_DECIMALS, PREPROCESSING_CONSTANTS_DER_THRESHOLD, PREPROCESSING_CONSTANTS_DESC, PREPROCESSING_CONSTANTS_STEP, PREPROCESSING_CONSTANTS_TITLE, PREPROCESSING_DISPLAY_CUT, PREPROCESSING_DISPLAY_CUT_WIDTH, PREPROCESSING_DISPLAY_DESC, PREPROCESSING_DISPLAY_INFO_HEIGHT, PREPROCESSING_DISPLAY_INFO_WIDTH, PREPROCESSING_DISPLAY_THRESHOLD, PREPROCESSING_DISPLAY_THRESHOLD_VALUE, PREPROCESSING_DISPLAY_TITLE, PREPROCESSING_DISPLAY_WIDGET_TAB_TITLE, PREPROCESSING_DISPLAY_WIDTH_VALUE, PREPROCESSING_HEIGHT_INFORMATION_PARSER, PREPROCESSING_INFORMATION_TABLE_COLUMN_HEIGHT, PREPROCESSING_INFORMATION_TABLE_WIDTH, PREPROCESSING_TABLE_PADDING, PREPROCESSING_THESHOLD_CONTROLS_TITLE, PREPROCESSING_THRESHOLD_DESC, PREPROCESSING_THRESHOLD_FRAME_TITLE, PREPROCESSING_THRESHOLD_INFORMATION, PREPROCESSING_THRESHOLD_LOAD, PREPROCESSING_THRESHOLD_PERCENTAGE, PREPROCESSING_THRESHOLD_SAVE, PREPROCESSING_THRESHOLD_SPIN_WIDTH, PREPROCESSING_THRESHOLD_SUFFIX, PREPROCESSSING_ERROR_THRESHOLD_IMAGE, VIDEO_PLAYER_BG_COLOR
from CONSTANTS import MAX_PIXEL_VALUE, NUMBER_OF_CONNECTED_COMPONENTS
from MessageBox import ErrorBox, InformationBox
from Preprocessing.CommonButtons import LowerButtons
from utils import convert2QT, getConnectedComponents, getThreshvalues, resizeFrame
from PyQt5.QtCore import pyqtSignal, pyqtSlot


class GeneralConstants(QWidget):

    constants_update = pyqtSignal()

    def __init__(self, process_controls, parent=None):
        super().__init__(parent)

        # Objects PREPROCESSING_DERIVATIVE_THRESHOLD_STEP
        self.process_controls = process_controls
        self.der_thresh_valid = process_controls['der_threshold']

        # Widgets
        group = QGroupBox(self)
        self.title = QLabel(PREPROCESSING_CONSTANTS_TITLE, group)
        self.desc = QLabel(PREPROCESSING_CONSTANTS_DESC, group)
        self.der_thresh = QDoubleSpinBox(group)
        self.der_thresh_apply = QPushButton('Apply', group)
        

        # init routines

        self.der_thresh.setValue(self.der_thresh_valid)

        self.title.setStyleSheet(
            'font-weight: bold; font-size: 20px;'
        )
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        self.der_thresh.setDecimals(PREPROCESSING_CONSTANTS_DECIMALS)
        self.der_thresh.setSingleStep(PREPROCESSING_CONSTANTS_STEP)


        # Signals and Slots
        self.der_thresh.valueChanged.connect(self.validateThreshold)
        self.der_thresh_apply.clicked.connect(self.apply)


        # Layout

        layout = QVBoxLayout()

        # Group
        group_layout = QFormLayout()
        group_layout.addRow(self.title)
        group_layout.addRow(self.desc)
        group_layout.addRow(PREPROCESSING_CONSTANTS_DER_THRESHOLD, self.der_thresh)
        group_layout.addRow(self.der_thresh_apply)

        group.setLayout(group_layout)

        # General layout
        layout.addWidget(group)
        layout.addStretch(1)
        self.setLayout(layout)

    def forceUpdate(self):
        self.der_thresh.setValue(self.process_controls['der_threshold'])

    def validateThreshold(self):
        der_threshold = self.der_thresh.value()
        if(der_threshold > 0):
            self.der_thresh_valid = der_threshold
            return True

        else:
            self.der_thresh.setValue(self.dder_thresh_valid)
            message = ErrorBox('Invalid threshold value. Cannot be lower than zero!')
            message.exec_()
            return False
        
    def apply(self):
        self.process_controls['der_threshold'] = self.der_thresh_valid
        self.constants_update.emit()
