import math
import sys
import os
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QFormLayout, QSpinBox
from PyQt5.QtGui import QPixmap, QColor, QImage
from GUI_CONSTANTS import MOUSE_EVENT_PIXEL_OFFSET, VIDEO_PLAYER_BG_COLOR
from utils import convert2QT

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


    def drawLine(self, x_cord):
        # Copy the frame to show
        draw_frame = self.frame.copy()

        # Get coordinates for center line
        height = self.resize_dict['original'][0]
        cv2.line(draw_frame, (x_cord, 0), (x_cord, height), (0, 255, 0), thickness=2)
        self.updateFrame(draw_frame)
    
    
    def mouseMoveEvent(self, event):
        x_cord = self.unScaleCord(event.x())
        # Draw the center line on the frame
        self.drawLine(x_cord)

        # Update Spinbox to value
        self.ButtonsWidget.updateCenterlinePos(x_cord)

    def getSizeDict(self):
        return self.resize_dict



        

class PreprocessingButtonsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Objects

        #Widgets
        self.center_line = QSpinBox(self)
        self.width = QSpinBox(self)

        # Init routines


        # Signals and Slots

        # Layout
        layout = QFormLayout()
        layout.addRow('Center Line (x coordinate):', self.center_line)
        layout.addRow('Width of Area of Interest:', self.width)


        self.setLayout(layout)

    def initSpinsBoxes(self, min, max):
        self.initSpinBox(min, max, self.center_line)

    def initSpinBox(self, min, max, box):
        box.setMinimum(min)
        box.setMaximum(max)
        

    def updateCenterlinePos(self, value):
        self.center_line.setValue(value)

if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = PreprocessingWidget()
    widget.setFrame('/media/mauricio/SSD_Mauricio/sp_lamp/sp_lamp_mix_tolueno_isooctano_1/1__23105690__20220909_120322743_0000.tiff')
    widget.show()
    sys.exit(app.exec_())