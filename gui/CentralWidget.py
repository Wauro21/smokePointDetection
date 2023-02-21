import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from LoadWidget import LoadWidget
from VideoPlayer import FrameHolder
from PlotWidget import PlotWidget
from GUI_CONSTANTS import FrameTypes
__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'

class CentralWidget(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)

        # Objects 
        self.video_path = None
        

        # -> Control dictionary 
        self.process_controls = {
            'core_%': 0,
            'contour_%': 0,
            'cut': None,
            'bboxes': False,
            'centroids': False, 
            'h': None,
            'H': None,
            'display': FrameTypes.FRAME,

        }


        # Widgets
        self.LoadWidget = LoadWidget(self)
        self.VideoWidget = FrameHolder(self.process_controls, self)
        self.PlotWidget = PlotWidget(self)
        
        # -> Temporal
        self.prueba = QPushButton('demo', self)
        self.original = QPushButton('Original', self)
        self.gray = QPushButton('Gray', self)

        # Init routines
        self.prueba.setEnabled(False)

        # Signals and Slots
        self.LoadWidget.path_signal.connect(self.setPrefix)
        self.LoadWidget.cut_info.connect(self.updateCutInfo)
        self.prueba.clicked.connect(self.requestPlayback)
        self.original.clicked.connect(lambda: self.demo(FrameTypes.FRAME))
        self.gray.clicked.connect(lambda: self.demo(FrameTypes.GRAY))

        # Layout
        # -> Demo layout
        layout = QVBoxLayout()
        layout.addWidget(self.LoadWidget)
        layout.addWidget(self.VideoWidget)
        layout.addWidget(self.prueba)
        layout.addWidget(self.PlotWidget)
        # Demo buttons
        test = QHBoxLayout()
        test.addWidget(self.original)
        test.addWidget(self.gray)

        layout.addLayout(test)
        

        self.setLayout(layout)

    def updateCutInfo(self):
        self.process_controls['cut'] = self.LoadWidget.getCutInfo()

    def setPrefix(self, video_path):
        self.video_path = video_path
        self.prueba.setEnabled(True)

    def requestPlayback(self):
        self.VideoWidget.startPlayback(self.video_path, self.PlotWidget.update)

    def demo(self, value):
        self.process_controls['display'] = value


if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = CentralWidget()
    widget.show()
    sys.exit(app.exec_())