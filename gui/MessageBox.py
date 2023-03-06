import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QGroupBox, QLabel, QFormLayout, QVBoxLayout, QWidget, QPushButton

from GUI_CONSTANTS import PREPROCESSING_DISPLAY_CUT, PREPROCESSING_DISPLAY_CUT_WIDTH, PREPROCESSING_DISPLAY_THRESHOLD, PREPROCESSING_DISPLAY_THRESHOLD_VALUE, PREPROCESSING_DISPLAY_WIDTH_VALUE

__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'



class ErrorBox(QMessageBox):
    
    def __init__(self, error_e, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Critical)
        self.setText('<b>An error has ocurred!</b>')
        self.setInformativeText(str(error_e))
        self.setWindowTitle('Error!')


class WarningBox(QMessageBox):
    def __init__(self, warning, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Warning)
        self.setText('<b>Warning:</b>')
        self.setInformativeText(warning)
        self.setWindowTitle('Warning!')

class InformationBox(QMessageBox):
    def __init__(self, info, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Information)
        self.setText('<b>Information:</b>')
        self.setInformativeText(info)
        self.setWindowTitle('Information!')

class LoadBox(QMessageBox):
    def __init__(self, info, process_controls, parent=None):
        super().__init__(parent)
        self.process_controls = process_controls
        self.setIcon(QMessageBox.Information)
        self.setText('<b>Information:</b>')
        self.setInformativeText(info)
        self.setWindowTitle('Information!')

        # Display the loaded presets 
        group = QGroupBox(self)
        self.cut_left = QLabel(group)
        self.cut_right = QLabel(group)
        self.cut_width = QLabel(group)
        self.core = QLabel(group)
        self.contour = QLabel(group)

        group_layout = QFormLayout()
        group_layout.addRow(PREPROCESSING_DISPLAY_CUT.format('left'), self.cut_left)
        group_layout.addRow(PREPROCESSING_DISPLAY_CUT.format('right'), self.cut_right)
        group_layout.addRow(PREPROCESSING_DISPLAY_CUT_WIDTH, self.cut_width)
        group_layout.addRow(PREPROCESSING_DISPLAY_THRESHOLD.format('Core'), self.core)
        group_layout.addRow(PREPROCESSING_DISPLAY_THRESHOLD.format('Contour'), self.contour)
        group.setLayout(group_layout)

        self.updateInfo()
        
        self.layout().addWidget(group)
    
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




if __name__ == '__main__':
    app = QApplication([])
    widget = ErrorBox('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla porta est interdum, vulputate metus et, bibendum dui. Nunc fermentum tincidunt mi nec semper')
    widget.show()
    sys.exit(app.exec_())