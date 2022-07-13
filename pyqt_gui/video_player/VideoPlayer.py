import cv2
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
import sys
import numpy as np

# Thread reader
class VideoReader(QThread):
    change_frame_signal = pyqtSignal(np.ndarray)

    def run(self):
        video = cv2.VideoCapture('test.mp4')
        while video.isOpened():
            ret, frame = video.read()
            if(ret):
                self.change_frame_signal.emit(frame)
            else:
                print('End of video in thread-reader')
                break

class FrameHolder(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)
        # Frame-Holder label
        self.frame_label = QLabel(self)
        gray_fill = QPixmap(680,480)
        gray_fill.fill(QColor('darkGray'))
        self.frame_label.setPixmap(gray_fill)


        self.top_text = QLabel('This is a video test')

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.top_text)
        vbox.addWidget(self.frame_label)
        # Add to widget
        self.setLayout(vbox)

        # Read video from thread
        self.thread = VideoReader()
        self.thread.change_frame_signal.connect(self.update_frame)
        self.thread.start()

    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        qt_img = self.convert2Qt(frame)
        self.frame_label.setPixmap(qt_img)

    def convert2Qt(self, cv_img):
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch*w
        converted = QImage(rgb_img, w, h, bytes_per_line, QImage.Format_RGB888)
        converted = converted.scaled(680,480,Qt.KeepAspectRatio)
        return QPixmap.fromImage(converted)

if __name__ == '__main__':
    app = QApplication([])
    test = FrameHolder()
    test.show()
    sys.exit(app.exec_())
