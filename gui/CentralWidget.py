import sys
import os

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from LoadWidget import LoadWidget
from VideoPlayer import FrameHolder

__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'

class CentralWidget(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)

        self.video_path = None
        
        # Objects 

        # Widgets
        self.LoadWidget = LoadWidget(self)
        self.VideoWidget = FrameHolder(self)
        self.prueba = QPushButton('demo', self)

        # Init routines
        self.prueba.setEnabled(False)

        # Signals and Slots
        self.LoadWidget.path_signal.connect(self.setPrefix)
        self.prueba.clicked.connect(self.requestPlayback)


        # Layout
        # -> Demo layout
        layout = QVBoxLayout()
        layout.addWidget(self.LoadWidget)
        layout.addWidget(self.VideoWidget)
        layout.addWidget(self.prueba)

        self.setLayout(layout)

    def setPrefix(self, video_path):
        self.video_path = video_path
        self.prueba.setEnabled(True)

    def requestPlayback(self):
        self.VideoWidget.startPlayback(self.video_path)



if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = CentralWidget()
    widget.show()
    sys.exit(app.exec_())