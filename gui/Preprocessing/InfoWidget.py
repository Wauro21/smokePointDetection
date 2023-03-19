import json
import datetime
from PyQt5.QtWidgets import QGroupBox, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QFileDialog
from PyQt5 import QtCore
from gui.GUI_CONSTANTS import PREPROCESSING_DISPLAY_CENTROID_TOL, PREPROCESSING_DISPLAY_CENTROID_TOL_VALUE, PREPROCESSING_DISPLAY_CUT, PREPROCESSING_DISPLAY_CUT_WIDTH, PREPROCESSING_DISPLAY_DERIVATIVE_THRESHOLD, PREPROCESSING_DISPLAY_DERIVATIVE_THRESHOLD_VALUE, PREPROCESSING_DISPLAY_DESC, PREPROCESSING_DISPLAY_FACTOR, PREPROCESSING_DISPLAY_FACTOR_VALUE, PREPROCESSING_DISPLAY_THRESHOLD, PREPROCESSING_DISPLAY_THRESHOLD_VALUE, PREPROCESSING_DISPLAY_TITLE, PREPROCESSING_DISPLAY_WIDGET_TAB_TITLE, PREPROCESSING_DISPLAY_WIDTH_VALUE, PREPROCESSING_THRESHOLD_SAVE
from gui.Preprocessing.GeneralConstants import GeneralConstants


class DisplaySettings(QWidget):

    def __init__(self, process_controls, parent=None):
        super().__init__(parent)

        # Objects
        self.tab_title = PREPROCESSING_DISPLAY_WIDGET_TAB_TITLE
        self.process_controls = process_controls

        # Widgets
        self.constants_widget = GeneralConstants(process_controls, self)
        general_group = QGroupBox(self)
        self.title = QLabel(PREPROCESSING_DISPLAY_TITLE, general_group)
        self.desc = QLabel(PREPROCESSING_DISPLAY_DESC, general_group)
        # -> Group box
        group = QGroupBox(general_group)
        self.cut_left = QLabel(group)
        self.cut_right = QLabel(group)
        self.cut_width = QLabel(group)
        self.core = QLabel(group)
        self.contour = QLabel(group)
        self.factor = QLabel(group)
        self.der_thresh = QLabel(group)
        self.centroid_tol = QLabel(group)

        self.labels = [self.cut_left, self.cut_right, self.cut_width, self.core, self.contour, self.factor, self.der_thresh, self.centroid_tol]

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
        #group.setFixedSize(PREPROCESSING_DISPLAY_INFO_WIDTH, PREPROCESSING_DISPLAY_INFO_HEIGHT)

        # Signals and Slots
        self.save.clicked.connect(self.save2JSON)
        self.constants_widget.constants_update.connect(self.updateInfo)

        # Layout
        layout = QHBoxLayout()

        # -> General group layout
        general_group_layout = QVBoxLayout()

        # -> Group layout
        group_layout = QFormLayout()
        group_layout.addRow(PREPROCESSING_DISPLAY_CUT.format('left'), self.cut_left)
        group_layout.addRow(PREPROCESSING_DISPLAY_CUT.format('right'), self.cut_right)
        group_layout.addRow(PREPROCESSING_DISPLAY_CUT_WIDTH, self.cut_width)
        group_layout.addRow(PREPROCESSING_DISPLAY_THRESHOLD.format('Core'), self.core)
        group_layout.addRow(PREPROCESSING_DISPLAY_THRESHOLD.format('Contour'), self.contour)
        group_layout.addRow(PREPROCESSING_DISPLAY_FACTOR, self.factor)
        group_layout.addRow(PREPROCESSING_DISPLAY_DERIVATIVE_THRESHOLD, self.der_thresh)
        group_layout.addRow(PREPROCESSING_DISPLAY_CENTROID_TOL, self.centroid_tol)
        group.setLayout(group_layout)

        # -> Lower buttons
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.apply)
        buttons.addWidget(self.save)
        buttons.addStretch(1)

        general_group_layout.addWidget(self.title)
        general_group_layout.addWidget(self.desc)

        # -> Center info
        center = QHBoxLayout()
        center.addStretch(1)
        center.addWidget(group)
        center.addStretch(1)

        general_group_layout.addLayout(center)

        general_group_layout.addLayout(buttons)
        general_group_layout.addStretch(1)

        general_group.setLayout(general_group_layout)

        layout.addWidget(self.constants_widget)
        layout.addWidget(general_group)
        self.setLayout(layout)

    def forceUpdate(self):
        self.constants_widget.forceUpdate()
        self.updateInfo()

    def getTitle(self):
        return self.tab_title

    def applyHandler(self, function):
        self.apply.clicked.connect(function)

    def save2JSON(self):

        # Generate threshold dict
        save_dict = self.process_controls['controls']

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
        cut_dict = self.process_controls['controls']['cut']
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

        self.core.setText(PREPROCESSING_DISPLAY_THRESHOLD_VALUE.format(self.process_controls['controls']['core_%']))
        self.contour.setText(PREPROCESSING_DISPLAY_THRESHOLD_VALUE.format(self.process_controls['controls']['contour_%']))

        # -> Camera calibration
        self.factor.setText(PREPROCESSING_DISPLAY_FACTOR_VALUE.format(self.process_controls['controls']['conv_factor']))

        # -> Set constants values
        self.der_thresh.setText(PREPROCESSING_DISPLAY_DERIVATIVE_THRESHOLD_VALUE.format(self.process_controls['controls']['der_threshold']))
        self.centroid_tol.setText(PREPROCESSING_DISPLAY_CENTROID_TOL_VALUE.format(self.process_controls['controls']['centroid_tol']))

        