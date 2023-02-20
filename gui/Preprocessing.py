import math
import sys
import os
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout
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
        self.frame_label = QLabel(self)

        # Init routines
        self.defaultFrame()

        # Signals and Slots

        #Layout
        layout = QHBoxLayout()
        layout.addWidget(self.frame_label)

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



    def mouseMoveEvent(self, event):

        # Copy the frame to show
        draw_frame = self.frame.copy()

        # Get coordinates for center line
        x_center = self.unScaleCord(event.x())

        cv2.line(draw_frame, (x_center, -10), (x_center, 1000), (0, 255, 0), thickness=2)
 
        self.updateFrame(draw_frame)


if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = PreprocessingWidget()
    widget.setFrame('/media/mauricio/SSD_Mauricio/sp_lamp/sp_lamp_mix_tolueno_isooctano_1/1__23105690__20220909_120322743_0000.tiff')
    widget.show()
    sys.exit(app.exec_())