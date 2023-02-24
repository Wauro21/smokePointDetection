import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from LoadWidget import LoadWidget
from Frameplayer.VideoPlayer import FrameHolder
from Plot.PlotWidget import PlotWidget
from GUI_CONSTANTS import FrameTypes
from Plot.PlotHolder import PlotHolder
__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'

class CentralWidget(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)

        # Objects 
        self.video_path = None
        

        # -> Control dictionary 
        self.process_controls = {
            'core_%': 2,
            'contour_%': 1,
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
        # -> Plots 
        self.HeightPlot = PlotWidget('Height Analysis', 'Frames [-]', 'Height [px]', ['Flame Height', 'Tip Height'], self)
        self.CentroidPlot = PlotWidget('TBI','', '', [] , self)
        self.Plotholder = PlotHolder([self.HeightPlot, self.CentroidPlot],self)

        
        # -> Temporal
        self.prueba = QPushButton('demo', self)

        # Init routines
        self.prueba.setEnabled(False)

        # Signals and Slots
        self.LoadWidget.path_signal.connect(self.setPrefix)
        self.LoadWidget.cut_info.connect(self.updateCutInfo)
        self.prueba.clicked.connect(self.requestPlayback)

        # Layout
        # -> Demo layout
        layout = QVBoxLayout()
        layout.addWidget(self.LoadWidget)

        # -> Video and plot area
        video_plot_layout = QHBoxLayout()
        video_plot_layout.addWidget(self.VideoWidget)
        video_plot_layout.addWidget(self.Plotholder)
        layout.addLayout(video_plot_layout)
        
        layout.addWidget(self.prueba)
        
        self.setLayout(layout)

    def updateCutInfo(self):
        self.process_controls['cut'] = self.LoadWidget.getCutInfo()

    def setPrefix(self, video_path):
        self.video_path = video_path
        self.prueba.setEnabled(True)

    def requestPlayback(self):
        self.VideoWidget.startPlayback(self.video_path, self.HeightPlot.update)

    def demo(self, value):
        self.process_controls['display'] = value


if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = CentralWidget()
    widget.show()
    sys.exit(app.exec_())