import os
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5 import QtCore
from GUI_CONSTANTS import PREPROCESSING_AREA_INFORMATION_PARSER, PREPROCESSING_HEIGHT_INFORMATION_PARSER, PREPROCESSING_THESHOLD_CONTROLS_TITLE, PREPROCESSING_THRESHOLD_FRAME_TITLE, PREPROCESSING_THRESHOLD_INFORMATION, PREPROCESSING_THRESHOLD_PERCENTAGE, PREPROCESSING_THRESHOLD_SUFFIX, PREPROCESSSING_ERROR_THRESHOLD_IMAGE, VIDEO_PLAYER_BG_COLOR
from CONSTANTS import MAX_PIXEL_VALUE, NUMBER_OF_CONNECTED_COMPONENTS
from MessageBox import ErrorBox
from utils import convert2QT, getConnectedComponents, getThreshvalues, resizeFrame
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt

class ThresholdWidget(QWidget):
    start_signal = pyqtSignal()
    def __init__(self, process_controls,  parent=None):
        
        super().__init__(parent)

        # Objects 
        self.frame = None
        self.process_controls = process_controls

        # Widgets 
        self.core_frame = ThresholdFrame(self.process_controls, 'Core', 'core_%', self)
        self.core_controls = ThresholdControls('Core', 'core_%', self.process_controls, self)
        self.contour_frame = ThresholdFrame(self.process_controls, 'Contour', 'contour_%', self)
        self.contour_controls = ThresholdControls('Contour', 'contour_%', self.process_controls, self)


        # Init routines
        

        # Signals and Slots
        # -> Invalid area update signals
        self.core_frame.invalid_area.connect(self.core_controls.invalidValue)
        self.contour_frame.invalid_area.connect(self.contour_controls.invalidValue)
        # -> Update frame signals
        self.core_controls.update_frame.connect(lambda: self.core_frame.setFrame(self.frame))
        self.contour_controls.update_frame.connect(lambda: self.contour_frame.setFrame(self.frame))

        # -> Update info
        self.core_frame.info_update.connect(self.core_controls.updateInfo)
        self.contour_frame.info_update.connect(self.contour_controls.updateInfo)

        # Layout
        layout = QHBoxLayout()

        layout.addWidget(self.core_frame)
        layout.addWidget(self.contour_frame)

        # -> Controls
        controls = QVBoxLayout()
        controls.addWidget(self.core_controls)
        controls.addWidget(self.contour_controls)

        layout.addLayout(controls)

        self.setLayout(layout)

    def setFrame(self, path):
        self.frame = path
        self.core_frame.setFrame(self.frame)
        self.contour_frame.setFrame(self.frame)


class ThresholdControls(QWidget):
    update_frame = pyqtSignal()
    def __init__(self, title, key, process_controls, parent=None):
        super().__init__(parent)

        # objects
        self.key = key
        self.process_controls = process_controls

        # widgets
        self.title = QLabel(PREPROCESSING_THESHOLD_CONTROLS_TITLE.format(title), self)
        self.threshold = QSpinBox(self)
        self.info_title = QLabel(PREPROCESSING_THRESHOLD_INFORMATION ,self)
        self.info_table = QTableWidget(self)
        
        # init routines
        self.threshold.setSuffix(PREPROCESSING_THRESHOLD_SUFFIX)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet(
            'font-weight: bold; font-size: 15px'
        )


        # -> Table init
        self.info_table.setRowCount(2)
        self.info_table.setColumnCount(1)
        self.info_table.setVerticalHeaderLabels(['Height', 'Area'])
        self.info_table.horizontalHeader().setVisible(False)
        
        self.info_table.setItem(0,0, QTableWidgetItem(PREPROCESSING_HEIGHT_INFORMATION_PARSER.format('-')))
        self.info_table.setItem(1,0, QTableWidgetItem(PREPROCESSING_AREA_INFORMATION_PARSER.format('-')))
        self.info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Signals and Slots
        self.threshold.valueChanged.connect(self.updateValue)

        # Layout

        layout = QVBoxLayout()

        # -> Main controls 
        main_controls = QFormLayout()
        main_controls.addRow(PREPROCESSING_THRESHOLD_PERCENTAGE.format(title), self.threshold)

        layout.addWidget(self.title)
        layout.addLayout(main_controls)
        layout.addWidget(self.info_title)
        layout.addWidget(self.info_table)

        self.setLayout(layout)
    
    @pyqtSlot(list)
    def updateInfo(self, values):
        height, area = values
        self.info_table.setItem(0,0, QTableWidgetItem(PREPROCESSING_HEIGHT_INFORMATION_PARSER.format(height)))
        self.info_table.setItem(1,0, QTableWidgetItem(PREPROCESSING_AREA_INFORMATION_PARSER.format(area)))


    def updateValue(self):
        self.process_controls[self.key] = self.threshold.value()
        self.update_frame.emit()

    @pyqtSlot(int)
    def invalidValue(self, old_valid):
        self.threshold.setValue(old_valid)
        message = ErrorBox(PREPROCESSSING_ERROR_THRESHOLD_IMAGE)
        message.exec_()





class ThresholdFrame(QWidget):

    invalid_area = pyqtSignal(int)
    info_update = pyqtSignal(list)
    
    def __init__(self, process_controls, title, key, parent=None):
        
        super().__init__(parent)

        # objects
        self.frame_path = None
        self.process_controls = process_controls
        self.key = key


        # Widgets
        self.frame = QLabel(self)
        self.frame_title = QLabel(PREPROCESSING_THRESHOLD_FRAME_TITLE.format(title), self)

        # init routines 
        self.frame_title.setAlignment(QtCore.Qt.AlignCenter)
        self.defaultFrame()

        self.frame_title.setStyleSheet(
            'font-weight: bold; font-size: 15px;'
        )

        # Slots and Signals

        # layout 

        layout = QVBoxLayout()

        layout.addWidget(self.frame_title)
        layout.addWidget(self.frame)

        self.setLayout(layout)

    def setFrame(self, frame_path):

        self.frame_path = frame_path
        
        # Load cv2 image
        frame = cv2.imread(frame_path, 0)
        
        # -> Use the cut information
        cut_info = self.process_controls['cut']
        if(cut_info):
            frame = frame[:, cut_info['left']: cut_info['right']]

        # -> Core frame
        thresh_value = getThreshvalues(self.process_controls[self.key])
        _, thresholded = cv2.threshold(frame, thresh_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
        thresholded_cc = getConnectedComponents(thresholded, NUMBER_OF_CONNECTED_COMPONENTS)

        if (thresholded_cc['area'] >= 0):

            thresh_mask = resizeFrame(thresholded_cc['cmask'])

            # Conver 2QT
            qt_thresholded = convert2QT(thresh_mask)
        
            # Set the frame 
            self.frame.setPixmap(qt_thresholded)

            # Set the info, emit the info_update
            info_height = thresholded_cc['h']
            info_area = thresholded_cc['area']
            self.info_update.emit([info_height, info_area])
            

            # Save last valid value
            self.last_valid_value = self.process_controls[self.key]
            
            
        else:
            # Emit error signal and send the last valid value
            self.invalid_area.emit(self.last_valid_value)

    def defaultFrame(self):
            gray_fill = QPixmap(200, 480)
            gray_fill.fill(QColor(VIDEO_PLAYER_BG_COLOR))
            self.frame.setPixmap(gray_fill)
            self.frame_path = None
