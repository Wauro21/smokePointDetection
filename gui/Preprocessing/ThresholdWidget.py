import os
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox, QPushButton
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5 import QtCore
from GUI_CONSTANTS import GUI_RED_ERROR_BG, PREPROCESSING_AREA_THRESHOLD_INFO, PREPROCESSING_HEIGHT_THRESHOLD_INFO, PREPROCESSING_KEY_DICT, PREPROCESSING_START_ERROR, PREPROCESSING_THRESHOLD_FRAME_TITLE, PREPROCESSING_THRESHOLD_PERCENTAGE, PREPROCESSSING_ERROR_THRESHOLD_IMAGE, VIDEO_PLAYER_BG_COLOR
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
        self.processControls = process_controls

        # Widgets
        self.coreThresh = ThresholdViewer('Core', process_controls, self)
        self.contourThresh = ThresholdViewer('Contour', process_controls, self)
        self.start_run = QPushButton('Start run', self)

        # Init routines

        # Signals and Slots
        self.start_run.clicked.connect(self.startHandler)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.coreThresh)
        layout.addWidget(self.contourThresh)
        self.setLayout(layout)

    def startHandler(self):

        # Validate values : Core must be lower than contour
        if(self.processControls['core_%'] < self.processControls['contour_%']):
            self.start_signal.emit()

        else:
            message = ErrorBox(PREPROCESSING_START_ERROR)
            message.exec_()



    def setFrame(self, frame_path):
        self.frame = frame_path
        self.coreThresh.setFrame(self.frame)
        self.contourThresh.setFrame(self.frame)

class ThresholdViewer(QWidget):
    def __init__(self, title, process_controls, parent=None):
        super().__init__(parent)

        # Objects
        self.process_controls = process_controls
        self.key = title.lower()
        self.last_valid_value = None

        # Widgets
        self.frame_holder = QLabel(self)
        title_text = PREPROCESSING_THRESHOLD_FRAME_TITLE.format(title)
        self.title  = QLabel(title_text, self)
        self.threshold = QSpinBox(self)
        self.info_title = QLabel('Area of interest information', self)
        self.area = QLabel('- px*px', self)
        self.height = QLabel('- px', self)
        
        # init routines
        self.defaultFrame()

        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet(
            'font-weight: bold; font-size: 15px'
        )

        self.info_title.setAlignment(QtCore.Qt.AlignCenter)
        self.info_title.setStyleSheet(
            'font-weight: bold'
        )

        # Slots and Signals
        self.threshold.valueChanged.connect(self.updateValue)

        # layout
        layout = QVBoxLayout()

        # -> Controls
        controls = QFormLayout()
        spin_title = PREPROCESSING_THRESHOLD_PERCENTAGE.format(title)
        controls.addRow(spin_title, self.threshold)
        controls.addRow(self.info_title)
        controls.addRow('Area: ', self.area)
        controls.addRow('Height: ', self.height)

        # -> Central area
        central = QHBoxLayout()
        central.addWidget(self.frame_holder)
        central.addLayout(controls)

        # -> General
        layout.addWidget(self.title)
        layout.addLayout(central)

        self.setLayout(layout)

    def updateValue(self):
        # Update threshold percentage
        key = PREPROCESSING_KEY_DICT.format(self.key)
        self.process_controls[key] = self.threshold.value()
        self.setFrame(self.frame)

    def defaultFrame(self):
            gray_fill = QPixmap(200, 480)
            gray_fill.fill(QColor(VIDEO_PLAYER_BG_COLOR))
            self.frame_holder.setPixmap(gray_fill)
            self.frame = None


    def setFrame(self, frame_path):
        
        self.frame = frame_path
        # Load cv2 image
        frame = cv2.imread(frame_path, 0)
        
        # -> Use the cut information
        cut_info = self.process_controls['cut']
        if(cut_info):
            frame = frame[:, cut_info['left']: cut_info['right']]

        # -> Core frame
        key = PREPROCESSING_KEY_DICT.format(self.key)
        thresh_value = getThreshvalues(self.process_controls[key])
        _, thresholded = cv2.threshold(frame, thresh_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
        thresholded_cc = getConnectedComponents(thresholded, NUMBER_OF_CONNECTED_COMPONENTS)

        if (thresholded_cc['area'] >= 0):

            thresh_mask = resizeFrame(thresholded_cc['cmask'])

            # Conver 2QT
            qt_thresholded = convert2QT(thresh_mask)
        
            # Set the frame 
            self.frame_holder.setPixmap(qt_thresholded)

            # Set the info
            self.area.setText(PREPROCESSING_AREA_THRESHOLD_INFO.format(thresholded_cc['area']))
            self.height.setText(PREPROCESSING_HEIGHT_THRESHOLD_INFO.format(thresholded_cc['h']))

            # Save last valid value
            self.last_valid_value = self.threshold.value()
            
            
        else:
            self.threshold.setValue(self.last_valid_value)
            
            message = ErrorBox(PREPROCESSSING_ERROR_THRESHOLD_IMAGE)
            message.exec_()



if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = ThresholdViewer('wow')
    widget.setFrame('/media/mauricio/SSD_Mauricio/sp_lamp/sp_lamp_mix_tolueno_isooctano_1/1__23105690__20220909_120322743_0000.tiff')
    widget.show()
    sys.exit(app.exec_())