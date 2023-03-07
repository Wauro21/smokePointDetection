import os
import sys
import cv2
import json
from datetime import datetime, date
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QProgressBar, QGroupBox
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5 import QtCore
from GUI_CONSTANTS import INFORMATION_BAR_ELAPSED_FIELD, INFORMATION_BAR_ELAPSED_LABEL, INFORMATION_BAR_OPERATION_LABEL, INFORMATION_LABELS_WIDTH, INFORMATION_PROCESSED_CENTROID_DECIMALS, INFORMATION_PROCESSED_CENTROID_LABEL, INFORMATION_PROCESSED_CONTOUR_LABEL, INFORMATION_PROCESSED_CORE_LABEL, INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, INFORMATION_PROCESSED_ROW_CENTROID, INFORMATION_PROCESSED_ROW_H_POINTS, INFORMATION_PROCESSED_ROW_INVALID_FRAMES, INFORMATION_PROCESSED_ROW_NUMBER_FRAMES, INFORMATION_PROCESSED_ROW_TIME, INFORMATION_PROCESSED_ROW_TIP_POINTS, INFORMATION_PROCESSED_THRESHOLD_FIELD, INFORMATION_TAB_DISPLAY_HEIGHT, INFORMATION_TAB_DISPLAY_WIDTH, PLOT_WIDGET_WIDTH, PREPROCESSING_AREA_INFORMATION_PARSER, PREPROCESSING_HEIGHT_INFORMATION_PARSER, PREPROCESSING_INFORMATION_TABLE_COLUMN_HEIGHT, PREPROCESSING_INFORMATION_TABLE_WIDTH, PREPROCESSING_START_ERROR, PREPROCESSING_TABLE_PADDING, PREPROCESSING_THESHOLD_CONTROLS_TITLE, PREPROCESSING_THRESHOLD_DESC, PREPROCESSING_THRESHOLD_FRAME_TITLE, PREPROCESSING_THRESHOLD_INFORMATION, PREPROCESSING_THRESHOLD_LOAD, PREPROCESSING_THRESHOLD_PERCENTAGE, PREPROCESSING_THRESHOLD_SAVE, PREPROCESSING_THRESHOLD_SPIN_WIDTH, PREPROCESSING_THRESHOLD_SUFFIX, PREPROCESSSING_ERROR_THRESHOLD_IMAGE, VIDEO_PLAYER_BG_COLOR, VIDEO_PLAYER_WIDTH_DEFAULT, InformationStatus
from CONSTANTS import MAX_PIXEL_VALUE, NUMBER_OF_CONNECTED_COMPONENTS
from MessageBox import ErrorBox, InformationBox
from Preprocessing.CommonButtons import LowerButtons
from utils import convert2QT, getConnectedComponents, getThreshvalues, resizeFrame
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QTime


class InformationTab(QWidget):

    def __init__(self, process_controls, parent=None):
        super().__init__(parent)

        # Objects
        self.process_controls = process_controls
        self.title = 'Process Summary'

        # Widgets
        self.frame_info = FrameInformation(self)

        # Init 

        
        # Signals and Slots


        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.frame_info)

        self.setLayout(layout)

    def updateTabs(self, process_controls):
        self.frame_info.updateInformation(process_controls)

    def getTitle(self):
        return self.title

class FrameInformation(QWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)

        # Objects

        # Widgets
        self.title = 'DEMO'
        group = QGroupBox('Frame process summary',self)
        self.core = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.contour = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.n_frames = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.n_invalid_frames = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.centroid_reference = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.n_points_h = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.n_points_H = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.processing_time = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.labels = [self.n_frames, self.n_invalid_frames, self.centroid_reference, self.n_points_h, self.n_points_H, self.processing_time, self.core, self.contour]

        # init routines
        self.setFixedWidth(INFORMATION_TAB_DISPLAY_WIDTH)
        self.setFixedHeight(INFORMATION_TAB_DISPLAY_HEIGHT)
        group.setStyleSheet('QGroupBox { font-weight: bold;}')

        for label in self.labels:
            label.setStyleSheet(
                'margin-left:20px;'
            )
            label.setAlignment(QtCore.Qt.AlignRight)

        # Signals and Slots

        # Layout
        layout = QVBoxLayout()

        # -> info display
        display = QHBoxLayout(self)
        
        info_left = QFormLayout()
        info_left.addRow(INFORMATION_PROCESSED_CORE_LABEL, self.core)
        info_left.addRow(INFORMATION_PROCESSED_ROW_NUMBER_FRAMES, self.n_frames)
        info_left.addRow(INFORMATION_PROCESSED_ROW_INVALID_FRAMES, self.n_invalid_frames)
        info_left.addRow(INFORMATION_PROCESSED_ROW_H_POINTS, self.n_points_h)
        display.addLayout(info_left)

        info_right = QFormLayout()
        info_right.addRow(INFORMATION_PROCESSED_CONTOUR_LABEL, self.contour)
        info_right.addRow(INFORMATION_PROCESSED_ROW_TIME, self.processing_time)
        info_right.addRow(INFORMATION_PROCESSED_ROW_CENTROID, self.centroid_reference)
        info_right.addRow(INFORMATION_PROCESSED_ROW_TIP_POINTS, self.n_points_H)
        display.addLayout(info_right)


        group.setLayout(display)
        layout.addWidget(group)

        self.setLayout(layout)

    def updateInformation(self, process_controls):
        core = INFORMATION_PROCESSED_THRESHOLD_FIELD.format(process_controls['core_%'])
        contour = INFORMATION_PROCESSED_THRESHOLD_FIELD.format(process_controls['contour_%'])
        n_frames = str(process_controls['n_frames'])
        n_invalid_frames = str(process_controls['n_invalid_frames'])
        centroid = str(round(process_controls['centroid_ref_cord'], INFORMATION_PROCESSED_CENTROID_DECIMALS))
        last_time = str(process_controls['last_run_time'])
        h_points = str(len(process_controls['h']))
        H_points = str(len(process_controls['H']))

        self.core.setText(core)
        self.contour.setText(contour)
        self.n_frames.setText(n_frames)
        self.n_invalid_frames.setText(n_invalid_frames)
        self.centroid_reference.setText(INFORMATION_PROCESSED_CENTROID_LABEL.format(centroid))
        self.processing_time.setText(last_time)
        self.n_points_h.setText(h_points)
        self.n_points_H.setText(H_points)

        


class InformationBar(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)

        # Objects
        self.status = None
        self.last_steps = None
        self.start_time = None
        self.last_run = None

        # Widgets
        self.operation_label = QLabel(INFORMATION_BAR_OPERATION_LABEL, self)
        self.operation_field = QLabel(InformationStatus.IDLE.value, self)
        self.elapsed_label = QLabel(INFORMATION_BAR_ELAPSED_LABEL, self)
        self.elapsed_field = QLabel(INFORMATION_BAR_ELAPSED_FIELD.format(0,0,0), self)
        self.elapsed_time = QTimer(self)
        self.progress = QProgressBar(self)

        # init routines
        self.elapsed_time.setInterval(1000) # Change to setInterval

        self.operation_label.setStyleSheet(
            'font-weight: bold'
        )

        self.elapsed_label.setStyleSheet(
            'font-weight: bold'
        )

        self.progress.setFixedWidth(PLOT_WIDGET_WIDTH)
        self.operation_label.setFixedWidth(INFORMATION_LABELS_WIDTH)
        self.operation_field.setFixedWidth(INFORMATION_LABELS_WIDTH)
        self.elapsed_label.setFixedWidth(INFORMATION_LABELS_WIDTH)
        self.operation_field.setFixedWidth(INFORMATION_LABELS_WIDTH)

        # Slots and Signals
        self.elapsed_time.timeout.connect(self.updateTime)

        # Layout
        layout = QHBoxLayout()
        layout.addStretch(1)
        # -> Information
        info = QFormLayout()
        info.addRow(self.operation_label, self.operation_field)
        info.addRow(self.elapsed_label, self.elapsed_field)

        layout.addLayout(info)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def setStatus(self, status):
        self.status = status
        self.operation_field.setText(self.status.value)
        if(self.status is InformationStatus.FRAMES):
            # Start elapsed time 
            self.start()

        if(self.status is InformationStatus.FRAMES_DONE):
            # Restart the timer
            self.restart()


    def restart(self):
        self.last_run = self.elapsed_field.text()
        self.start_time = None
        self.elapsed_time.stop()
        self.setTimeLabel(0, 0, 0)

    def start(self):
        self.last_steps = 0
        self.start_time = datetime.now()
        self.elapsed_time.start()

    def updateTime(self):
        # Get current time 
        time = datetime.now()
        # Calculate elapsed
        elapsed = time -self.start_time
        sec = elapsed.seconds
        disp_sec = sec%60
        hours = sec // 3600
        minutes = (sec // 60) - (hours*60)
        self.setTimeLabel(hours, minutes, disp_sec)
        
    def setTimeLabel(self, hours, minutes, secs):
        time_string = INFORMATION_BAR_ELAPSED_FIELD.format(hours, minutes, secs)
        self.elapsed_field.setText(time_string)
        

    def stepBar(self, total):
        self.last_steps += 1
        value = 100*(self.last_steps/total)
        self.progress.setValue(value)

    def getLastTime(self):
        return self.last_run
