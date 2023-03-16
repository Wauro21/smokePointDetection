import os
import sys
import cv2
import json
import datetime
from PyQt5.QtWidgets import QGroupBox, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QTableWidget, QSpinBox, QTabWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from GUI_CONSTANTS import PLOT_WIDGET_DPI, PLOT_WIDGET_HEIGHT, PLOT_WIDGET_WIDTH, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_DESC, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG_FIELD, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD_FIELD, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARE_FIELD, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARE_SIDE, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARES, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_THRESHOLD, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_THRESHOLD_MAX, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_TITLE, PREPROCESSING_CAMERA_CALIBRATION_LOAD_DIALOG, PREPROCESSING_CAMERA_CALIBRATION_LOAD_IMAGE, PREPROCESSING_CAMERA_CALIBRATION_PLOT_FRAME_TITLE, PREPROCESSING_CAMERA_CALIBRATION_PX_MM_A_LABEL, PREPROCESSING_CAMERA_CALIBRATION_PX_MM_DEF_THRESH, PREPROCESSING_CAMERA_CALIBRATION_PX_MM_DESC, PREPROCESSING_CAMERA_CALIBRATION_PX_MM_TITLE, PREPROCESSING_CAMERA_CALIBRATION_THRESHOLD_FRAME_TITLE, PREPROCESSING_CAMERA_CALIBRATION_WIDGET_TAB_TITLE
from MessageBox import ErrorBox
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from Preprocessing.CommonButtons import LowerButtons
from CONSTANTS import MAX_PIXEL_VALUE


class CameraCalibration(QWidget):


    def __init__(self, process_controls,  parent=None):
        
        super().__init__(parent)

        # Objects 
        self.tab_title = PREPROCESSING_CAMERA_CALIBRATION_WIDGET_TAB_TITLE
        self.frame = None

        # Widgets 
        # -> Load image
        load_group = QGroupBox(self)
        self.load_img_des = QLabel('File:', load_group)
        self.load_display_img = QLineEdit(PREPROCESSING_CAMERA_CALIBRATION_LOAD_IMAGE, load_group)
        self.load_button = QPushButton('Open', load_group)

        # -> Plot images
        self.plot_tabs = QTabWidget(self)
        self.original_frame = ImagePlot(PREPROCESSING_CAMERA_CALIBRATION_PLOT_FRAME_TITLE, self.plot_tabs)
        self.threshold_frame = ImagePlot(PREPROCESSING_CAMERA_CALIBRATION_THRESHOLD_FRAME_TITLE, self.plot_tabs)

        # -> Controls 
        controls_group = QGroupBox(self)
        self.controls_title = QLabel(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_TITLE, controls_group)
        self.controls_desc = QLabel(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_DESC, controls_group)
        self.controls_squares = QSpinBox(controls_group)
        self.controls_threshold = QSpinBox(controls_group)
        self.controls_square_trace = QLabel(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARE_FIELD.format('-') ,controls_group)
        self.controls_square_avg = QLabel(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG_FIELD.format('-'), controls_group)
        self.controls_square_std = QLabel(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD_FIELD.format('-'), controls_group)
        self.controls_find_button = QPushButton('Process', controls_group)


        # -> Px mm group
        px_mm_group = QGroupBox(self)
        self.px_mm_title = QLabel(PREPROCESSING_CAMERA_CALIBRATION_PX_MM_TITLE, px_mm_group)
        self.px_mm_desc = QLabel(PREPROCESSING_CAMERA_CALIBRATION_PX_MM_DESC, px_mm_group)
        self.px_mm_field = QDoubleSpinBox(px_mm_group)

        # -> Lower buttons
        self.loweractions = LowerButtons(self)

        # Init routines
        
        # -> Load image
        self.load_display_img.setReadOnly(True)

        # -> Plot images
        self.plot_tabs.addTab(self.original_frame, self.original_frame.getTitle())
        self.plot_tabs.addTab(self.threshold_frame, self.threshold_frame.getTitle())

        # -> Controls 

        self.controls_title.setStyleSheet(
            'font-weight: bold'
        )
        self.controls_title.setWordWrap(True)
        self.controls_desc.setWordWrap(True)
        self.controls_threshold.setMaximum(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_THRESHOLD_MAX)
        self.controls_threshold.setValue(PREPROCESSING_CAMERA_CALIBRATION_PX_MM_DEF_THRESH)

        # Signals and Slots
        # -> Load image
        self.load_button.clicked.connect(self.getFile)


        # Layout
        layout = QHBoxLayout()

        # -> Load group
        load_group_layout = QHBoxLayout()
        load_group_layout.addWidget(self.load_img_des)
        load_group_layout.addWidget(self.load_display_img)
        load_group_layout.addWidget(self.load_button)
        load_group.setLayout(load_group_layout)

        # -> Controls group
        controls_group_layout = QVBoxLayout()
        controls_group_layout.addWidget(self.controls_title)
        controls_group_layout.addWidget(self.controls_desc)

        # -> Controls group: Spinboxes
        controls_spin = QFormLayout()
        controls_spin.addRow(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARES, self.controls_squares)
        controls_spin.addRow(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_THRESHOLD, self.controls_threshold)
        controls_spin.addRow(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARE_SIDE, self.controls_square_trace)
        controls_spin.addRow(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG, self.controls_square_avg)
        controls_spin.addRow(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD, self.controls_square_std)
        controls_spin.addRow(self.controls_find_button)

        controls_group_layout.addLayout(controls_spin)
        controls_group.setLayout(controls_group_layout)

        # -> px mm groupd
        px_mm_layout = QVBoxLayout()
        px_mm_layout.addWidget(self.px_mm_title)
        px_mm_layout.addWidget(self.px_mm_desc)

        px_mm_factor_layout = QFormLayout()
        px_mm_factor_layout.addRow(PREPROCESSING_CAMERA_CALIBRATION_PX_MM_A_LABEL, self.px_mm_field)

        px_mm_layout.addLayout(px_mm_factor_layout)
        px_mm_group.setLayout(px_mm_layout)


        # Left 
        left = QVBoxLayout()
        left.addWidget(load_group)
        left.addWidget(self.plot_tabs)

        # Right 
        right = QVBoxLayout()
        right.addWidget(controls_group)
        right.addWidget(px_mm_group)
        right.addWidget(self.loweractions)


        layout.addLayout(left)
        layout.addLayout(right)
        
        self.setLayout(layout)

    def getTitle(self):
        return self.tab_title


    def getFile(self):
        valid = False
        while not valid:
            fileDialog = QFileDialog(self, windowTitle=PREPROCESSING_CAMERA_CALIBRATION_LOAD_DIALOG)
            
            # This is a limitation of the pyqt framework, only files OR folders can be configured to be selected
            # by the native OS dialog. A workaround exists but doesnt look good as it doesn't uses the native dialog.
            fileDialog.setFileMode(QFileDialog.ExistingFile)

            if fileDialog.exec_():
                image_path = fileDialog.selectedFiles()[0]
                
                self.frame = cv2.imread(image_path, cv2.IMREAD_COLOR)
                if(self.frame is None):
                    message = ErrorBox('The selected file is not a valid image. Try with another!')
                    message.exec_()
                    valid = False

                else:
                    valid = True
                    self.updateFrame()
            else:
                # User pressed cancel
                break

    def updateFrame(self):
        
        # Update the original frame
        self.original_frame.plot(self.frame)

        # Update the threshold reference
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        tresh_val = round(MAX_PIXEL_VALUE*(self.controls_threshold.value()/100))
        print(tresh_val)
        ret, thresh = cv2.threshold(gray, tresh_val, MAX_PIXEL_VALUE,  cv2.THRESH_BINARY)

        self.threshold_frame.plot(thresh)

class ImagePlot(QWidget):

    def __init__(self, title, parent=None):
        super().__init__(parent)

        # Objects
        self.title = title

        # Widgets
        self.fig = Figure(figsize=(PLOT_WIDGET_WIDTH/PLOT_WIDGET_DPI, PLOT_WIDGET_HEIGHT/PLOT_WIDGET_DPI), dpi=PLOT_WIDGET_DPI)
        self.pltCanvas = FigureCanvas(self.fig)
        self.pltToolbar = NavigationToolbar(self.pltCanvas)

        # Init routines
        self.fig.subplots(nrows=1, ncols=1)
        self.axs = self.pltCanvas.figure.gca()
        self.setFixedHeight(PLOT_WIDGET_HEIGHT)
        self.setFixedWidth(PLOT_WIDGET_WIDTH)

        # Signals and Slots

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self.pltToolbar)
        layout.addWidget(self.pltCanvas)
        self.setLayout(layout)

    def getTitle(self):
        return self.title
    
    def plot(self, frame):

        # Set the image 
        self.axs.imshow(frame)
        self.pltCanvas.draw()