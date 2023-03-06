import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from Plot.CentroidPlot import CentroidPlotWidget
from LoadWidget import LoadWidget
from Frameplayer.VideoPlayer import FrameHolder
from Plot.ProcessPlot import ProcessPlotWidget
from GUI_CONSTANTS import FrameTypes, InformationStatus
from Plot.PlotHolder import PlotHolder
from Preprocessing.CutWidget import CutWidget
from Preprocessing.Preprocessing import PreprocessingWidget
from Preprocessing.ThresholdWidget import ThresholdWidget
from Preprocessing.InfoWidget import DisplaySettings
from RunInformation import InformationBar, InformationTab
__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'

class CentralWidget(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)

        # Objects 
        self.video_path = None
        self.demo_frame_path = None
        

        # -> Control dictionary 
        self.process_controls = {
            'n_frames': 0,
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
        self.LoadWidget = LoadWidget(self.process_controls, self)
        self.VideoWidget = FrameHolder(self.process_controls, self)
        # -> Preprocess : No parent so can be displayed as new window
        self.PreprocessingTabs = PreprocessingWidget()
        self.CutWindow = CutWidget(self.process_controls, self.PreprocessingTabs)
        self.ThresholdWindow = ThresholdWidget(self.process_controls, self.PreprocessingTabs)
        self.DisplayWindow = DisplaySettings(self.process_controls, self.PreprocessingTabs)

        # -> Plots 
        self.HeightPlot = ProcessPlotWidget('Height Analysis', 'Frames [-]', 'Height [px]', ['Flame Height', 'Core Height', 'Tip Height'], self)
        self.CentroidPlot = CentroidPlotWidget('Centroid Analysis', 'Frames [-]', 'X coordinate [px]')
        self.Plotholder = PlotHolder([self.HeightPlot, self.CentroidPlot],self)

        # -> Information bar
        self.infoBar = InformationBar(self)

        # Init routines
        self.PreprocessingTabs.addTab(self.CutWindow, 'Cut frame', True)
        self.PreprocessingTabs.addTab(self.ThresholdWindow, 'Threshold controls', False)
        self.PreprocessingTabs.addTab(self.DisplayWindow, 'Run settings', False)
        self.DisplayWindow.applyHandler(self.enableStart)
        self.LoadWidget.startHandler(self.requestStart)

        # Signals and Slots
        self.LoadWidget.path_signal.connect(self.setPrefix)
        self.LoadWidget.configureHandler(self.requestCutting)
        self.CutWindow.preprocess_done.connect(self.requestThreshold)
        self.ThresholdWindow.done_signal.connect(self.requestDisplay)
        self.VideoWidget.frame_process_done.connect(self.frameProcessDone)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.LoadWidget)

        # -> Video and plot area
        video_plot_layout = QHBoxLayout()
        video_plot_layout.addWidget(self.VideoWidget)
        video_plot_layout.addWidget(self.Plotholder)
        layout.addLayout(video_plot_layout)

        layout.addWidget(self.infoBar)
        
        self.setLayout(layout)

    def frameProcessDone(self):
        self.infoBar.setStatus(InformationStatus.FRAMES_DONE)

    def centroidSignalHandler(self, message):
        # Update centroid plot
        self.CentroidPlot.update(message)
        self.infoBar.stepBar(self.process_controls['n_frames'])
        

    def enableStart(self):
        self.PreprocessingTabs.requestClose()
        self.LoadWidget.startEnable()

    def requestDisplay(self):
        # Update run settings display
        self.DisplayWindow.updateInfo()
        self.PreprocessingTabs.setTabEnabled(2, True)
        self.PreprocessingTabs.setCurrentIndex(2)

    def requestStart(self):
        self.infoBar.setStatus(InformationStatus.FRAMES)
        self.requestPlayback()

    def requestThreshold(self):
        # Update run settings display
        self.DisplayWindow.updateInfo()
        
        # Set the frame
        self.ThresholdWindow.setFrame(self.demo_frame_path)
        self.PreprocessingTabs.setTabEnabled(1, True)
        self.PreprocessingTabs.setCurrentIndex(1)

    def requestCutting(self):
        # Set the frame for the process
        self.CutWindow.setFrame(self.demo_frame_path)
        #self.ThresholdWindow.setFrame(self.demo_frame_path)
        self.PreprocessingTabs.show()

    def updateCutInfo(self):
        self.process_controls['cut'] = self.LoadWidget.getCutInfo()

    def setPrefix(self, values):
        self.video_path, self.demo_frame_path = values

    def requestPlayback(self):
        self.VideoWidget.startPlayback(self.video_path, self.HeightPlot.update, self.centroidSignalHandler)

    def demo(self, value):
        self.process_controls['display'] = value


if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = CentralWidget()
    widget.show()
    sys.exit(app.exec_())