from PyQt5.QtWidgets import QGroupBox, QWidget, QLabel, QVBoxLayout, QFormLayout, QPushButton, QDoubleSpinBox, QSpinBox
from PyQt5 import QtCore
from gui.GUI_CONSTANTS import PREPROCESSING_CONSTANTS_CENTROID_TOLERANCE, PREPROCESSING_CONSTANTS_CENTROID_TOLERANCE_SUFFIX, PREPROCESSING_CONSTANTS_DECIMALS, PREPROCESSING_CONSTANTS_DER_THRESHOLD, PREPROCESSING_CONSTANTS_DESC, PREPROCESSING_CONSTANTS_STEP, PREPROCESSING_CONSTANTS_TITLE
from gui.MessageBox import ErrorBox
from PyQt5.QtCore import pyqtSignal


class GeneralConstants(QWidget):

    constants_update = pyqtSignal()

    def __init__(self, process_controls, parent=None):
        super().__init__(parent)

        # Objects PREPROCESSING_DERIVATIVE_THRESHOLD_STEP
        self.process_controls = process_controls
        self.der_thresh_valid = self.process_controls['controls']['der_threshold']
        self.centroid_tol_valid = self.process_controls['controls']['centroid_tol']

        # Widgets
        group = QGroupBox(self)
        self.title = QLabel(PREPROCESSING_CONSTANTS_TITLE, group)
        self.desc = QLabel(PREPROCESSING_CONSTANTS_DESC, group)
        self.der_thresh = QDoubleSpinBox(group)
        self.centroid_reference = QSpinBox(group)
        self.apply_button = QPushButton('Apply', group)
        

        # init routines

        self.title.setStyleSheet(
            'font-weight: bold; font-size: 20px;'
        )
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        # -> Derivative threshold

        self.der_thresh.setDecimals(PREPROCESSING_CONSTANTS_DECIMALS)
        self.der_thresh.setSingleStep(PREPROCESSING_CONSTANTS_STEP)
        self.der_thresh.setValue(self.der_thresh_valid)

        # -> Centroid tolerance
        self.centroid_reference.setSuffix(PREPROCESSING_CONSTANTS_CENTROID_TOLERANCE_SUFFIX)
        self.centroid_reference.setValue(self.centroid_tol_valid)


        # Signals and Slots
        #self.der_thresh.valueChanged.connect(self.validateThreshold)
        self.apply_button.clicked.connect(self.apply)


        # Layout

        layout = QVBoxLayout()

        # Group
        group_layout = QFormLayout()
        group_layout.addRow(self.title)
        group_layout.addRow(self.desc)
        group_layout.addRow(PREPROCESSING_CONSTANTS_DER_THRESHOLD, self.der_thresh)
        group_layout.addRow(PREPROCESSING_CONSTANTS_CENTROID_TOLERANCE, self.centroid_reference)
        group_layout.addRow(self.apply_button)

        group.setLayout(group_layout)

        # General layout
        layout.addWidget(group)
        layout.addStretch(1)
        self.setLayout(layout)

    def forceUpdate(self):
        self.der_thresh.setValue(self.process_controls['controls']['der_threshold'])

    def validateCentroid(self):
        centroid_tol = self.centroid_reference.value()
        if(centroid_tol > 0):
            self.centroid_tol_valid = centroid_tol
            self.process_controls['controls']['centroid_tol'] = self.centroid_tol_valid
            return True
        else:
            self.centroid_reference.setValue(self.centroid_tol_valid)
            message = ErrorBox('Invalid centroid reference value. Cannot be lower than zero!')
            message.exec_()
            return False


    def validateThreshold(self):
        der_threshold = self.der_thresh.value()
        if(der_threshold > 0):
            self.der_thresh_valid = der_threshold
            self.process_controls['controls']['der_threshold'] = self.der_thresh_valid
            return True

        else:
            self.der_thresh.setValue(self.der_thresh_valid)
            message = ErrorBox('Invalid threshold value. Cannot be lower than zero!')
            message.exec_()
            return False
        
    def apply(self):
        self.validateThreshold()
        self.validateCentroid()

        self.constants_update.emit()

