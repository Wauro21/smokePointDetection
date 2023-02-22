import cv2
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QApplication
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
import sys
import numpy as np
from GUI_CONSTANTS import VIDEO_PLAYER_BG_COLOR, FrameTypes
from MessageBox import WarningBox
from Thread import VideoReader
from VideoButtons import VideoButtons
from utils import convert2QT
from PIL import Image


class FrameHolder(QWidget):
    
    def __init__(self, process_controls, parent=None):
        super().__init__(parent)

        self.thread = None
        self.process_controls = process_controls
        # Widgets 
        self.controls = VideoButtons(self)
        self.frame_label = QLabel(self)

        # Init routines
        self.initViewer()

        # Signals and Slots
        self.controls.frame_selection.connect(self.selectFrame)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.controls)
        layout.addWidget(self.frame_label)

        self.setLayout(layout)       
    
    @pyqtSlot(FrameTypes)
    def selectFrame(self, frame_code):
        self.process_controls['display'] = frame_code

    def initViewer(self):
        gray_fill = QPixmap(200, 480)
        gray_fill.fill(QColor(VIDEO_PLAYER_BG_COLOR))
        self.frame_label.setPixmap(gray_fill)
        

    def startPlayback(self, video_path, update_function):
        if(self.thread != None):
            warning = WarningBox('Playback thread is already busy playing other media. Close the program.')
            warning.exec_()
            return False


        self.thread = VideoReader(video_path, self.process_controls)
        self.thread.update_frame_signal.connect(self.updateLabel)
        self.thread.finished.connect(self.cleanThread)
        self.thread.values_signal.connect(update_function)
        self.thread.start()

        return True

    def cleanThread(self):
        self.thread = None


    @pyqtSlot(np.ndarray)
    def updateLabel(self, frame):
        # CLEAN CLEAN CLEANCLEAN CLEAN CLEANCLEAN CLEAN CLEANCLEAN CLEAN CLEANCLEAN CLEAN CLEAN
        #testing resize

        try:
            h, w, c = frame.shape
        except:
            h, w = frame.shape
            c = None
        ar = w/h
        nH = 480
        nW = round(ar*480)
        
        n_frame = cv2.resize(frame, (nW, nH))
        if(c):
            f_frame = np.ones((480, 200, c), np.uint8)
            f_frame[:,:,0] =  f_frame[:,:,0] *255
        else:
            f_frame = np.ones((480, 200), np.uint8)
            f_frame[:,:] =  f_frame[:,:] *255

        aH, aW = 0, (200 - nW)//2

        f_frame[aH:aH+nH, aW:aW+nW] = n_frame

        qt_img = convert2QT(f_frame, False)
        self.frame_label.setPixmap(qt_img)


if __name__ == '__main__':
    app = QApplication([])
    test = FrameHolder()
    test.startPlayback('/media/mauricio/SSD_Mauricio/SP_18_08_22/SP_20fps_1_5/Basler_acA2040-55uc__23734412__20220818_185407088_%04d.tiff')
    test.show()
    sys.exit(app.exec_())
