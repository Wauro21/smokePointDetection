import math
import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QFormLayout, QSpinBox, QPushButton
from PyQt5.QtGui import QPixmap, QColor, QImage
from GUI_CONSTANTS import MOUSE_EVENT_PIXEL_OFFSET, PREPROCESSING_DESC_MESSAGE, PREPROCESSING_LINES_WIDTH, PREPROCESSING_MINIMUM_WIDTH, PREPROCESSING_SCROLL_WIDTH_STEP, PREPROCESSING_TITLE_MESSAGE, PREPROCESSING_WIDTH_LINE_COLOR, PREPROCESSING_WINDOW_TITLE, PREPROESSING_CENTER_LINE_COLOR, VIDEO_PLAYER_BG_COLOR
from .CutButtonsWidget import CutButtonsWidget
from utils import convert2QT
from PyQt5.QtCore import pyqtSignal

class CutWidget(QWidget):
    
    preprocess_done = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Objects
        self.frame = None
        self.resize_dict = {
            'original': None,
            'scaled': None,
        }
        # Widgets
        self.ButtonsWidget = CutButtonsWidget(self)
        self.frame_label = QLabel(self)

        # Init routines
        self.defaultFrame()
        self.setWindowTitle(PREPROCESSING_WINDOW_TITLE)

        # Signals and Slots
        self.ButtonsWidget.update_frame.connect(self.updateAreaofInterest)
        self.ButtonsWidget.cut_signal.connect(self.preprocessingDone)

        #Layout
        layout = QHBoxLayout()
        layout.addWidget(self.frame_label)
        layout.addWidget(self.ButtonsWidget)

        self.setLayout(layout)

    def preprocessingDone(self):
        self.preprocess_done.emit()
        self.close()

    def getCutInfo(self):
        return self.ButtonsWidget.getCutDict()

    def defaultFrame(self):
        gray_fill = QPixmap(640, 480)
        gray_fill.fill(QColor(VIDEO_PLAYER_BG_COLOR))
        self.frame_label.setPixmap(gray_fill)
        self.frame = None

    def setFrame(self, frame_path):
        
        # Load cv2 image
        self.frame = cv2.imread(frame_path, -1)
        self.resize_dict['original'] = self.frame.shape
        # Conver 2QT
        qt_frame = convert2QT(self.frame)
        # Get size of the scaled frame
        self.resize_dict['scaled'] = (qt_frame.size().height(), qt_frame.size().width())

        # Set the frame 
        self.frame_label.setPixmap(qt_frame)

        # Init spinboxes with info from frame
        w_original =  self.resize_dict['original'][1]
        self.ButtonsWidget.initSpinsBoxes(0, w_original)


    def updateAreaofInterest(self):
        x_cord = self.ButtonsWidget.getCenterlinePos()
        width = self.ButtonsWidget.getAreaWidth()
        self.draweAreaofInterest(x_cord, width)

    def updateFrame(self, frame=None):
        if (frame is None):
            frame = self.frame
        # Convert 2QT
        qt_frame = convert2QT(frame)

        # Set the frame 
        self.frame_label.setPixmap(qt_frame)

    def unScaleCord(self, value):
        # Ws -> W
        # xS -> X
        return math.floor(value*self.resize_dict['original'][0] / self.resize_dict['scaled'][0])-MOUSE_EVENT_PIXEL_OFFSET


    def draweAreaofInterest(self, x_cord, width):
        # Copy the frame to show
        draw_frame = self.frame.copy()

        # Get coordinates for center line
        height = self.resize_dict['original'][0]

        # Calculate area width
        w = width // 2

        # Draw lines on frame
        # -> Center line
        cv2.line(draw_frame, (x_cord, 0), (x_cord, height), PREPROESSING_CENTER_LINE_COLOR, thickness=PREPROCESSING_LINES_WIDTH)
        
        # -> Width lines
        cv2.line(draw_frame, (x_cord-w, 0), (x_cord-w, height), PREPROCESSING_WIDTH_LINE_COLOR, thickness=PREPROCESSING_LINES_WIDTH)
        cv2.line(draw_frame, (x_cord+w, 0), (x_cord+w, height), PREPROCESSING_WIDTH_LINE_COLOR, thickness=PREPROCESSING_LINES_WIDTH)
        self.updateFrame(draw_frame)
    
    
    def mouseMoveEvent(self, event):
        x_cord = self.unScaleCord(event.x())
        self.ButtonsWidget.updateCenterlinePos(x_cord)

    def wheelEvent(self, event):
        # increment width in defined steps
        sign_step = np.sign(event.angleDelta().y())
        self.ButtonsWidget.mouseIncrementWidth(sign_step*PREPROCESSING_SCROLL_WIDTH_STEP)

    def getSizeDict(self):
        return self.resize_dict



if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = CutWidget()
    widget.setFrame('/media/mauricio/SSD_Mauricio/sp_lamp/sp_lamp_mix_tolueno_isooctano_1/1__23105690__20220909_120322743_0000.tiff')
    widget.show()
    sys.exit(app.exec_())