import os
import sys
import cv2
import numpy as np
import json
import datetime
from PyQt5.QtWidgets import QGroupBox, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QTableWidget, QSpinBox, QTabWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from GUI_CONSTANTS import PLOT_WIDGET_DPI, PLOT_WIDGET_HEIGHT, PLOT_WIDGET_WIDTH, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_DESC, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG_FIELD, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD_FIELD, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARE_SIDE, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARES, PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_TITLE, PREPROCESSING_CAMERA_CALIBRATION_CORNER_COLOR, PREPROCESSING_CAMERA_CALIBRATION_DEFAULT_FACTOR, PREPROCESSING_CAMERA_CALIBRATION_FACTOR, PREPROCESSING_CAMERA_CALIBRATION_LOAD_DIALOG, PREPROCESSING_CAMERA_CALIBRATION_LOAD_IMAGE, PREPROCESSING_CAMERA_CALIBRATION_LOAD_JSON_DIALOG, PREPROCESSING_CAMERA_CALIBRATION_MIN_SQUARE_SIDE, PREPROCESSING_CAMERA_CALIBRATION_MIN_SQUARES, PREPROCESSING_CAMERA_CALIBRATION_N_DECIMALS, PREPROCESSING_CAMERA_CALIBRATION_NO_CORNERS_ERROR, PREPROCESSING_CAMERA_CALIBRATION_PLOT_FRAME_TITLE, PREPROCESSING_CAMERA_CALIBRATION_PX_MM_A_LABEL, PREPROCESSING_CAMERA_CALIBRATION_PX_MM_DESC, PREPROCESSING_CAMERA_CALIBRATION_PX_MM_TITLE, PREPROCESSING_CAMERA_CALIBRATION_SAVE_DESC, PREPROCESSING_CAMERA_CALIBRATION_SAVE_TITLE, PREPROCESSING_CAMERA_CALIBRATION_SQUARE_SIDE_UNIT, PREPROCESSING_CAMERA_CALIBRATION_WIDGET_TAB_TITLE
from MessageBox import ErrorBox, InformationBox
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from Preprocessing.CommonButtons import LowerButtons
from CONSTANTS import MAX_PIXEL_VALUE


class CameraCalibration(QWidget):

    calibration_done = pyqtSignal()

    def __init__(self, process_controls,  parent=None):
        
        super().__init__(parent)

        # Objects 
        self.factor = PREPROCESSING_CAMERA_CALIBRATION_DEFAULT_FACTOR
        self.process_controls = process_controls
        self.tab_title = PREPROCESSING_CAMERA_CALIBRATION_WIDGET_TAB_TITLE
        self.frame = None

        # Widgets 
        # -> Load image
        load_group = QGroupBox(self)
        self.load_img_des = QLabel('File:', load_group)
        self.load_display_img = QLineEdit(PREPROCESSING_CAMERA_CALIBRATION_LOAD_IMAGE, load_group)
        self.load_button = QPushButton('Open', load_group)

        # -> Plot images
        self.original_frame = ImagePlot(PREPROCESSING_CAMERA_CALIBRATION_PLOT_FRAME_TITLE, self)

        # -> Controls 
        self.controls_group = QGroupBox(self)
        self.controls_title = QLabel(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_TITLE, self.controls_group)
        self.controls_desc = QLabel(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_DESC, self.controls_group)
        self.controls_squares = QSpinBox(self.controls_group)
        self.controls_square_trace = QDoubleSpinBox(self.controls_group)
        self.controls_square_avg = QLabel(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG_FIELD.format(0), self.controls_group)
        self.controls_square_std = QLabel(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD_FIELD.format(0), self.controls_group)
        self.controls_find_button = QPushButton('Process', self.controls_group)


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

        # -> Controls 

        self.controls_title.setStyleSheet(
            'font-weight: bold'
        )
        self.controls_title.setWordWrap(True)
        self.controls_desc.setWordWrap(True)
        self.controls_squares.setMinimum(PREPROCESSING_CAMERA_CALIBRATION_MIN_SQUARES)
        self.controls_square_trace.setMinimum(PREPROCESSING_CAMERA_CALIBRATION_MIN_SQUARE_SIDE)
        self.controls_group.setEnabled(False)
        self.controls_square_trace.setSuffix(PREPROCESSING_CAMERA_CALIBRATION_SQUARE_SIDE_UNIT)

        # -> px - mm
        self.px_mm_title.setStyleSheet(
            'font-weight: bold'
        )

        self.px_mm_field.setValue(self.factor)
        self.px_mm_field.setSuffix(PREPROCESSING_CAMERA_CALIBRATION_FACTOR)
        self.px_mm_field.setSingleStep(0.0001)
        self.px_mm_field.setDecimals(PREPROCESSING_CAMERA_CALIBRATION_N_DECIMALS)


        # Signals and Slots
        # -> Load image
        self.load_button.clicked.connect(self.getFile)

        # -> controls: process
        self.controls_find_button.clicked.connect(self.updateFrame)

        # -> convertion
        self.px_mm_field.valueChanged.connect(self.validateFactor)

        # -> Lower actions
        self.loweractions.apply.connect(self.apply)
        self.loweractions.save.connect(self.save2JSON)
        self.loweractions.load.connect(self.loadJSON)

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
        controls_spin.addRow(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARE_SIDE, self.controls_square_trace)
        controls_spin.addRow(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG, self.controls_square_avg)
        controls_spin.addRow(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD, self.controls_square_std)
        controls_spin.addRow(self.controls_find_button)

        controls_group_layout.addLayout(controls_spin)
        self.controls_group.setLayout(controls_group_layout)

        # -> px mm group
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
        left.addWidget(self.original_frame)

        # Right 
        right = QVBoxLayout()
        right.addWidget(self.controls_group)
        right.addWidget(px_mm_group)
        right.addWidget(self.loweractions)


        layout.addLayout(left)
        layout.addLayout(right)
        
        self.setLayout(layout)


    def forceUpdate(self):
        self.px_mm_field.setValue(self.process_controls['conv_factor'])

    def validateFactor(self):
        factor = self.px_mm_field.value()
        if(factor > 0):
            # Valid 
            self.factor = factor

        else:
            # Set the latest valid value and inform the user
            self.px_mm_field.setValue(self.factor)
            message = ErrorBox('Conversion factor cannot be zero or lower.')
            message.exec_()


    def loadJSON(self):
        fileDialog = QFileDialog(self, windowTitle=PREPROCESSING_CAMERA_CALIBRATION_LOAD_JSON_DIALOG)
        fileDialog.setFileMode(QFileDialog.ExistingFile)
        fileDialog.setNameFilter('*.json')

        if fileDialog.exec_():
            file = fileDialog.selectedFiles()
            
            # Check if json is valid
            with open(file[0], 'r') as json_file:
                json_dict = json.load(json_file)

                try:
                    factor = json_dict['conv_factor']
                    # Load the conv factor to the box
                    self.px_mm_field.setValue(factor)

                    # Inform user
                    message = InformationBox('Presets loaded!')
                    message.exec_()

                except:
                    message = ErrorBox('The provided JSON file is not in the correct format! Try with another file.')
                    message.exec_()


    def save2JSON(self):
        save_dict = {
            'conv_factor': self.factor,
        }

        # Save file dialog
        date = datetime.datetime.now()
        date = date.strftime('%d-%m-%Y_%H-%M-%S')

        fileDialog = QFileDialog(self, windowTitle=PREPROCESSING_CAMERA_CALIBRATION_SAVE_TITLE)
        save_file = fileDialog.getSaveFileName(
            self,
            PREPROCESSING_CAMERA_CALIBRATION_SAVE_DESC, 
            directory='camera_calibration_{}.json'.format(date),
            filter='*.json',
        )

        if(save_file[0]):
            # Save the actual file
            with open(save_file[0], 'w') as file:
                json.dump(save_dict, file)


    def apply(self):
        self.process_controls['conv_factor'] = self.factor
        self.calibration_done.emit()

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
                    self.load_display_img.setText(image_path)
                    self.controls_group.setEnabled(True)
                    self.loadFrame()
            else:
                # User pressed cancel
                break

    def updateFrame(self):

        # Convert frame to gray
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        # Get corners
        n_corners = (self.controls_squares.value()- 1)
        ret, corners = cv2.findChessboardCornersSB(gray, (n_corners, n_corners))

        # Found corners
        if(ret):
            sides = self.analyzeCorners(corners, n_corners)

            # Plot the image  and scatter the corners
            self.original_frame.plotScatter(self.frame, corners)

            # Update the side information
            side_avg = np.mean(list(sides.values()))
            side_std = np.std(list(sides.values()))

            # Set the labels
            self.controls_square_avg.setText(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG_FIELD.format(side_avg))
            self.controls_square_std.setText(PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD_FIELD.format(side_std))

            # Calculate convertion factor
            self.factor = (self.controls_square_trace.value() / side_avg)
            self.px_mm_field.setValue(self.factor)
        else:
            message = ErrorBox(PREPROCESSING_CAMERA_CALIBRATION_NO_CORNERS_ERROR)
            message.exec_()


    def analyzeCorners(self, corners, n_corners):

        sides = {}
        for i in range(n_corners-1):
            for j in range(n_corners-1):
                # Get vertices

                x_1 = corners[i*n_corners+j][0][0]
                y_1 = corners[i*n_corners+j][0][1]

                x_2 = corners[i*n_corners+j+1][0][0]
                y_2 = corners[i*n_corners+j+1][0][1]

                x_3 = corners[(i+1)*n_corners+j][0][0]
                y_3 = corners[(i+1)*n_corners+j][0][1]

                x_4 = corners[(i+1)*n_corners+j+1][0][0]
                y_4 = corners[(i+1)*n_corners+j+1][0][1]

                # Average all the vertices 
                a = x_2 - x_1
                b = y_4 - y_2
                c = x_4 - x_3 
                d = y_3 - y_1
                
                l = (a + b + c + d) // 4

                sides[i,j] = l
        
        return sides

    def loadFrame(self):
        
        # Update the original frame
        self.original_frame.plot(self.frame)    

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
        # Clean previous image
        self.axs.cla()
        # Set the image 
        self.axs.imshow(frame)
        self.pltCanvas.draw()


    def plotScatter(self, frame, corners):
        # Clean previous image
        self.axs.cla()
        # Plot the frame
        self.axs.imshow(frame)
        # Scatter the values
        self.axs.scatter(corners[:,:, 0], corners[:,:, 1], color=PREPROCESSING_CAMERA_CALIBRATION_CORNER_COLOR)
        self.pltCanvas.draw()