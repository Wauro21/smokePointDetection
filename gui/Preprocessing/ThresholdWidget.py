import os
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QFormLayout, QSpinBox, QPushButton
from PyQt5.QtGui import QPixmap, QColor, QImage

from GUI_CONSTANTS import VIDEO_PLAYER_BG_COLOR
from CONSTANTS import MAX_PIXEL_VALUE
from utils import convert2QT, getThreshvalues, resizeFrame


class ThresholdWidget(QWidget):

    def __init__(self, process_controls,  parent=None):
        
        super().__init__(parent)

        # Objects 
        self.frame = None
        self.coreFrame = None
        self.contourFrame = None
        self.processControls = process_controls

        # Widgets
        self.core_label = QLabel(self)
        self.contour_label = QLabel(self)

        # Init routines
        self.defaultFrame()

        # Signals and Slots

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.core_label)
        layout.addWidget(self.contour_label)
        self.setLayout(layout)

    def defaultFrame(self):
        gray_fill = QPixmap(200, 480)
        gray_fill.fill(QColor(VIDEO_PLAYER_BG_COLOR))
        self.core_label.setPixmap(gray_fill)
        self.contour_label.setPixmap(gray_fill)
        self.frame = None


# -> NOT IMPLEMENTED
    def setFrame(self, frame_path):
        
        # Load cv2 image
        self.frame = cv2.imread(frame_path, 0)
        
        # -> Use the cut information
        cut_info = self.processControls['cut']
        if(cut_info):
            self.frame = self.frame[:, cut_info['left']: cut_info['right']]

        # -> Core frame
        core_value = getThreshvalues(self.processControls['core_%'])
        _, core = cv2.threshold(self.frame, core_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
        core = resizeFrame(core)
        # -> Contour 
        contour_value = getThreshvalues(self.processControls['contour_%'])
        _, contour = cv2.threshold(self.frame, contour_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
        contour = resizeFrame(contour)

        # Conver 2QT
        qt_core = convert2QT(core)
        qt_contour = convert2QT(contour)
       
        # Set the frame 
        self.core_label.setPixmap(qt_core)
        self.contour_label.setPixmap(qt_contour)


if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = ThresholdWidget()
    widget.setFrame('/media/mauricio/SSD_Mauricio/sp_lamp/sp_lamp_mix_tolueno_isooctano_1/1__23105690__20220909_120322743_0000.tiff')
    widget.show()
    sys.exit(app.exec_())