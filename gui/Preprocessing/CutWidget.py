import math
import sys
import os
import cv2
import numpy as np
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide2.QtGui import QPixmap, QColor
from gui.GUI_CONSTANTS import MOUSE_EVENT_PIXEL_OFFSET, PREPROCESSING_AUTO_CUT_PADDING, PREPROCESSING_AUTO_CUT_THRESHOLD_PERCENTAGE, PREPROCESSING_CUT_WIDGET_TAB_TITLE, PREPROCESSING_LINES_WIDTH, PREPROCESSING_SCROLL_WIDTH_STEP, PREPROCESSING_WIDTH_LINE_COLOR, PREPROCESSING_WINDOW_TITLE, PREPROESSING_CENTER_LINE_COLOR, VIDEO_PLAYER_BG_COLOR
from core.CONSTANTS import MAX_PIXEL_VALUE, NUMBER_OF_CONNECTED_COMPONENTS
from gui.MessageBox import ErrorBox
from .CutButtonsWidget import CutButtonsWidget
from core.utils import convert2QT, getConnectedComponents
from PySide2.QtCore import Signal

class CutWidget(QWidget):
    
    preprocess_done = Signal()

    def __init__(self, process_controls, parent=None):
        super().__init__(parent)

        # Objects
        self.tab_title = PREPROCESSING_CUT_WIDGET_TAB_TITLE
        self.process_controls = process_controls
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
        self.ButtonsWidget.autoHandler(self.autoCut)

        #Layout
        layout = QHBoxLayout()

        # -> Left 
        left = QVBoxLayout()
        left.addWidget(self.frame_label)
        left.addStretch(1)

        # -> right
        right = QVBoxLayout()
        right.addWidget(self.ButtonsWidget)
        right.addStretch(1)

        layout.addLayout(left)
        layout.addLayout(right)

        self.setLayout(layout)

    def getTitle(self):
        return self.tab_title

    def validateCutinfo(self):

        # Apply cut to the frame
        frame = self.frame.copy()
        cut_info = self.getCutInfo()
        frame = frame[:, cut_info['left']: cut_info['right']]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Get CC to check if area is not null
        ret, thresh = cv2.threshold(gray, 0, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
        thresholded_cc = getConnectedComponents(thresh, NUMBER_OF_CONNECTED_COMPONENTS)
        area = thresholded_cc['area']

        if(area > 0):
            return True
        
        else:
            message = ErrorBox('Selection results in a null image area. Try again.')
            message.exec_()
            return False
        
    def forceUpdate(self):
        width = (self.process_controls['controls']['cut']['right'] - self.process_controls['controls']['cut']['left'])
        center = self.process_controls['controls']['cut']['left'] + (width//2)
        
        self.ButtonsWidget.updateWidth(width)
        self.ButtonsWidget.updateCenterlinePos(center)


    def preprocessingDone(self):
        if(self.validateCutinfo()):
            self.process_controls['controls']['cut'] = self.getCutInfo()
            self.preprocess_done.emit()

    def getCutInfo(self):
        return self.ButtonsWidget.getCutDict()

    def defaultFrame(self):
        gray_fill = QPixmap(640, 480)
        gray_fill.fill(QColor(VIDEO_PLAYER_BG_COLOR))
        self.frame_label.setPixmap(gray_fill)
        self.frame = None

    def setFrame(self, frame_path, autocut=True):
        
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

        # Autocut 
        if(autocut):
            self.autoCut()
        else:
            self.updateAreaofInterest()


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
    

    def autoCut(self):

        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        ret, thresh = cv2.threshold(frame, PREPROCESSING_AUTO_CUT_THRESHOLD_PERCENTAGE, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
        # Get cc of the frame
        cc = getConnectedComponents(thresh, NUMBER_OF_CONNECTED_COMPONENTS)

        # Calculate the middle of the flame
        x = cc['x']
        width = cc['w']
        center = x + width//2
        self.ButtonsWidget.updateCenterlinePos(center)

        # Calculate the width with padding
        width += PREPROCESSING_AUTO_CUT_PADDING
        self.ButtonsWidget.updateWidth(width)

if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = CutWidget()
    widget.setFrame('/media/mauricio/SSD_Mauricio/sp_lamp/sp_lamp_mix_tolueno_isooctano_1/1__23105690__20220909_120322743_0000.tiff')
    widget.show()
    sys.exit(app.exec_())