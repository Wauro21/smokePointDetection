import os
import sys
import cv2
import json
import datetime
from PyQt5.QtWidgets import QHeaderView, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QGroupBox
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5 import QtCore
from GUI_CONSTANTS import PREPROCESSING_AREA_INFORMATION_PARSER, PREPROCESSING_HEIGHT_INFORMATION_PARSER, PREPROCESSING_INFORMATION_TABLE_COLUMN_HEIGHT, PREPROCESSING_INFORMATION_TABLE_WIDTH, PREPROCESSING_START_ERROR, PREPROCESSING_TABLE_PADDING, PREPROCESSING_THESHOLD_CONTROLS_TITLE, PREPROCESSING_THRESHOLD_DESC, PREPROCESSING_THRESHOLD_FRAME_TITLE, PREPROCESSING_THRESHOLD_INFORMATION, PREPROCESSING_THRESHOLD_LOAD, PREPROCESSING_THRESHOLD_PERCENTAGE, PREPROCESSING_THRESHOLD_SAVE, PREPROCESSING_THRESHOLD_SPIN_WIDTH, PREPROCESSING_THRESHOLD_SUFFIX, PREPROCESSING_THRESHOLD_WIDGET_TAB_TITLE, PREPROCESSSING_ERROR_THRESHOLD_IMAGE, VIDEO_PLAYER_BG_COLOR
from CONSTANTS import MAX_PIXEL_VALUE, NUMBER_OF_CONNECTED_COMPONENTS
from MessageBox import ErrorBox, InformationBox
from Preprocessing.CommonButtons import LowerButtons
from utils import convert2QT, getConnectedComponents, getThreshvalues, resizeFrame
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class ThresholdWidget(QWidget):
    done_signal = pyqtSignal()
    def __init__(self, process_controls,  parent=None):
        
        super().__init__(parent)

        # Objects 
        self.tab_title = PREPROCESSING_THRESHOLD_WIDGET_TAB_TITLE
        self.frame = None
        self.process_controls = process_controls

        # Widgets 
        self.desc = QLabel(PREPROCESSING_THRESHOLD_DESC, self)
        self.core_frame = ThresholdFrame(self.process_controls, 'Core', 'core_%', self)
        self.core_controls = ThresholdControls('Core', 'core_%', self.process_controls, self)
        self.contour_frame = ThresholdFrame(self.process_controls, 'Contour', 'contour_%', self)
        self.contour_controls = ThresholdControls('Contour', 'contour_%', self.process_controls, self)
        self.lower_buttons = LowerButtons(self)


        # Init routines
        self.desc.setWordWrap(True)
        self.desc.setStyleSheet(
            'font-weight: bold'
        )


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

        # -> lower buttons actions
        self.lower_buttons.apply.connect(self.applyThresh)
        self.lower_buttons.save.connect(self.save2JSON)
        self.lower_buttons.load.connect(self.loadJSON)

        # Layout
        layout = QHBoxLayout()

        layout.addWidget(self.core_frame)
        layout.addWidget(self.contour_frame)

        # -> Controls
        controls = QVBoxLayout()
        controls.addWidget(self.core_controls)
        controls.addWidget(self.contour_controls)
        controls.addWidget(self.desc)
        controls.addWidget(self.lower_buttons)

        layout.addLayout(controls)

        self.setLayout(layout)

    def getTitle(self):
        return self.tab_title

    def applyThresh(self):

        # Check if values are valid
        if(self.process_controls['core_%'] > self.process_controls['contour_%']):
            self.done_signal.emit()

        else: 
            message = ErrorBox(PREPROCESSING_START_ERROR)
            message.exec_()



    def setFrame(self, path):
        self.frame = path
        self.core_frame.setFrame(self.frame)
        self.contour_frame.setFrame(self.frame)

    def save2JSON(self):

        # Generate threshold dict
        save_dict = {
            'core_%': self.process_controls['core_%'],
            'contour_%': self.process_controls['contour_%']
        }

        # Save file dialog
        date = datetime.datetime.now()
        date = date.strftime('%d-%m-%Y_%H-%M-%S')

        fileDialog = QFileDialog(self, windowTitle=PREPROCESSING_THRESHOLD_SAVE)
        save_file = fileDialog.getSaveFileName(
            self,
            PREPROCESSING_THRESHOLD_SAVE, 
            directory='threshold_values_{}.json'.format(date),
            filter='*.json',
        )

        if(save_file[0]):
            # Save the actual file
            with open(save_file[0], 'w') as file:
                json.dump(save_dict, file)

    def loadJSON(self):
        fileDialog = QFileDialog(self, windowTitle=PREPROCESSING_THRESHOLD_LOAD)
        fileDialog.setFileMode(QFileDialog.ExistingFile)
        fileDialog.setNameFilter('*.json')

        if fileDialog.exec_():
            file = fileDialog.selectedFiles()
            
            # Check if json is valid
            with open(file[0], 'r') as json_file:
                json_dict = json.load(json_file)

                try:
                    core = json_dict['core_%']
                    contour = json_dict['contour_%']
                    self.core_controls.loadValues(core)
                    self.contour_controls.loadValues(contour)

                    # Inform user
                    message = InformationBox('Presets loaded!')
                    message.exec_()
                except:
                    message = ErrorBox('The provided JSON file is not in the correct format! Try with another file.')
                    message.exec_()


class ThresholdControls(QWidget):
    update_frame = pyqtSignal()
    def __init__(self, title, key, process_controls, parent=None):
        super().__init__(parent)

        # objects
        self.key = key
        self.process_controls = process_controls

        # widgets
        group = QGroupBox(self)
        self.title = QLabel(PREPROCESSING_THESHOLD_CONTROLS_TITLE.format(title), group)
        self.threshold = QDoubleSpinBox(group)
        self.info_title = QLabel(PREPROCESSING_THRESHOLD_INFORMATION ,group)
        self.info_table = QTableWidget(group)
        
        # init routines
        self.threshold.setSuffix(PREPROCESSING_THRESHOLD_SUFFIX)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet(
            'font-weight: bold; font-size: 15px'
        )

        self.info_title.setAlignment(QtCore.Qt.AlignCenter)
        self.info_title.setStyleSheet(
            'font-weight: bold;'
        )

        self.threshold.setFixedWidth(PREPROCESSING_THRESHOLD_SPIN_WIDTH)


        # -> Table init
        self.info_table.setRowCount(2)
        self.info_table.setColumnCount(1)
        self.info_table.setVerticalHeaderLabels(['Height', 'Area'])
        self.info_table.horizontalHeader().setVisible(False)
        
        self.info_table.setItem(0,0, QTableWidgetItem(PREPROCESSING_HEIGHT_INFORMATION_PARSER.format('-')))
        self.info_table.setItem(1,0, QTableWidgetItem(PREPROCESSING_AREA_INFORMATION_PARSER.format('-')))
        self.info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # -> Adjust table dimentions: Width
        table_header = self.info_table.verticalHeader()
        table_header.setStyleSheet(
            'font-weight: bold;'
        )
        table_header.setSectionResizeMode(QHeaderView.Fixed)
        table_header.setFixedWidth(PREPROCESSING_INFORMATION_TABLE_WIDTH//2)


        # -> Adjust table dimentions: Height
        n_rows = self.info_table.rowCount()
        for row in range(n_rows):
            self.info_table.setRowHeight(row, PREPROCESSING_INFORMATION_TABLE_COLUMN_HEIGHT)

        self.info_table.setFixedSize(PREPROCESSING_INFORMATION_TABLE_WIDTH, n_rows*PREPROCESSING_INFORMATION_TABLE_COLUMN_HEIGHT+ PREPROCESSING_TABLE_PADDING)
        

        # Signals and Slots
        self.threshold.valueChanged.connect(self.updateValue)

        # Layout

        layout = QVBoxLayout()

        # -> Main controls 
        main_controls = QFormLayout()
        main_controls.addRow(PREPROCESSING_THRESHOLD_PERCENTAGE.format(title), self.threshold)

        # -> table center
        table_layout = QHBoxLayout()
        table_layout.addStretch(1)
        table_layout.addWidget(self.info_table)
        table_layout.addStretch(1)

        # Group 
        group_layout = QVBoxLayout()
        group_layout.addWidget(self.title)
        group_layout.addLayout(main_controls)
        group_layout.addWidget(self.info_title)
        group_layout.addLayout(table_layout)
        group.setLayout(group_layout)

        # General Layout
        layout.addWidget(group)
        self.setLayout(layout)
    
    @pyqtSlot(list)
    def updateInfo(self, values):
        height, area = values
        self.info_table.setItem(0,0, QTableWidgetItem(PREPROCESSING_HEIGHT_INFORMATION_PARSER.format(height)))
        self.info_table.setItem(1,0, QTableWidgetItem(PREPROCESSING_AREA_INFORMATION_PARSER.format(area)))


    def updateValue(self):
        self.process_controls[self.key] = self.threshold.value()
        self.update_frame.emit()

    def loadValues(self, value):
        self.threshold.setValue(value)

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

        if (thresholded_cc['area'] > 0):

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
