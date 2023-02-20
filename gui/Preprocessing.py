import math
import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QFormLayout, QSpinBox, QPushButton
from PyQt5.QtGui import QPixmap, QColor, QImage
from GUI_CONSTANTS import MOUSE_EVENT_PIXEL_OFFSET, PREPROCESSING_MINIMUM_WIDTH, PREPROCESSING_SCROLL_WIDTH_STEP, VIDEO_PLAYER_BG_COLOR
from utils import convert2QT
from PyQt5.QtCore import pyqtSignal

class PreprocessingWidget(QWidget):
    def __init__(self, parent=None):
        
        super().__init__(parent)

        # Objects
        self.frame = None
        self.resize_dict = {
            'original': None,
            'scaled': None,
        }
        # Widgets
        self.ButtonsWidget = PreprocessingButtonsWidget(self)
        self.frame_label = QLabel(self)

        # Init routines
        self.defaultFrame()

        # Signals and Slots
        self.ButtonsWidget.update_frame.connect(self.updateAreaofInterest)

        #Layout
        layout = QHBoxLayout()
        layout.addWidget(self.frame_label)
        layout.addWidget(self.ButtonsWidget)

        self.setLayout(layout)


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
        print(self.resize_dict)

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

        # Calculate width of area
        w = width // 2

        # Draw lines on frame
        cv2.line(draw_frame, (x_cord, 0), (x_cord, height), (0, 255, 0), thickness=2)
        cv2.line(draw_frame, (x_cord-w, 0), (x_cord-w, height), (0, 0, 255), thickness=2)
        cv2.line(draw_frame, (x_cord+w, 0), (x_cord+w, height), (0, 0, 255), thickness=2)
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



        

class PreprocessingButtonsWidget(QWidget):
    update_frame = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        # Status 
        self.center_line_status = True
        self.width_status = True

        # Objects

        #Widgets
        self.center_line = QSpinBox(self)
        self.width = QSpinBox(self)
        self.lock_center_line = QPushButton('Lock')
        self.lock_width = QPushButton('Lock')

        # Init routines


        # Signals and Slots
        self.center_line.valueChanged.connect(lambda: self.update_frame.emit())
        self.width.valueChanged.connect(lambda: self.update_frame.emit())
        self.lock_center_line.clicked.connect(self.handleCenterLineControls)
        self.lock_width.clicked.connect(self.handleWidthControls)
        # Layout
        layout = QFormLayout()

        # -> Center line controls
        c_line_layout = QHBoxLayout()
        c_line_layout.addWidget(self.center_line)
        c_line_layout.addWidget(self.lock_center_line)

        # -> Width controsl
        width_layout = QHBoxLayout()
        width_layout.addWidget(self.width)
        width_layout.addWidget(self.lock_width)

        layout.addRow('Center Line (x coordinate):', c_line_layout)
        layout.addRow('Width of Area of Interest:', width_layout)


        self.setLayout(layout)

    def handleCenterLineControls(self):
        self.center_line_status = not self.center_line_status
        self.center_line.setEnabled(self.center_line_status)

    def handleWidthControls(self):
        self.width_status = not self.width_status
        self.width.setEnabled(self.width_status)

    def getCenterlinePos(self):
        return self.center_line.value()

    def getAreaWidth(self):
        return self.width.value()

    def initSpinsBoxes(self, min, max):
        self.initSpinBox(min, max, self.center_line)
        self.initSpinBox(PREPROCESSING_MINIMUM_WIDTH, max, self.width)

    def initSpinBox(self, min, max, box):
        box.setMinimum(min)
        box.setMaximum(max)
        

    def updateCenterlinePos(self, value):
        if(self.center_line.isEnabled()):
            self.center_line.setValue(value)

    def mouseIncrementWidth(self, step):
        if(self.width.isEnabled()):
            # get actual value from box
            a_width = self.width.value()
            # get max and min
            s_max = self.width.maximum()
            s_min = self.width.minimum()

            temp = a_width + step
            if(temp >= s_max):
                self.width.setValue(s_max)

            elif(temp <= s_min):
                self.width.setValue(s_min)

            else:
                self.width.setValue(temp)

if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = PreprocessingWidget()
    widget.setFrame('/media/mauricio/SSD_Mauricio/sp_lamp/sp_lamp_mix_tolueno_isooctano_1/1__23105690__20220909_120322743_0000.tiff')
    widget.show()
    sys.exit(app.exec_())