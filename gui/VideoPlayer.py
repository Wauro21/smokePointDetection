import cv2
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
import sys
import numpy as np
from Constants import VIDEO_PLAYER_BG_COLOR
from MessageBox import WarningBox

class VideoReader(QThread):

    update_frame_signal = pyqtSignal(np.ndarray)
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        
    def run(self):
        media = cv2.VideoCapture(self.video_path, 0)
        
        while media.isOpened():
            ret, frame = media.read()
            if(not ret):
                break
            self.update_frame_signal.emit(frame)


class FrameHolder(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.thread = None

        # Widgets 
        self.frame_label = QLabel(self)

        # Init routines
        
        gray_fill = QPixmap(480, 640)
        gray_fill.fill(QColor(VIDEO_PLAYER_BG_COLOR))
        self.frame_label.setPixmap(gray_fill)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.frame_label)

        self.setLayout(layout)       
        

    def startPlayback(self, video_path):
        if(self.thread != None):
            warning = WarningBox('Playback thread is already busy playing other media. Close the program.')
            warning.exec_()
            return False


        self.thread = VideoReader(video_path)
        self.thread.update_frame_signal.connect(self.updateLabel)
        self.thread.finished.connect(self.cleanThread)
        self.thread.start()

        return True

    def cleanThread(self):
        self.thread = None


    @pyqtSlot(np.ndarray)
    def updateLabel(self, frame):
        qt_img = self.convert2QT(frame)
        self.frame_label.setPixmap(qt_img)

    def convert2QT(self, cv_img):
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch*w
        converted = QImage(rgb_img, w, h, bytes_per_line, QImage.Format_RGB888)
        converted = converted.scaled(680,480,Qt.KeepAspectRatio)
        return QPixmap.fromImage(converted)

if __name__ == '__main__':
    app = QApplication([])
    test = FrameHolder()
    test.startPlayback('/media/mauricio/SSD_Mauricio/SP_18_08_22/SP_20fps_1_5/Basler_acA2040-55uc__23734412__20220818_185407088_%04d.tiff')
    test.show()
    sys.exit(app.exec_())
