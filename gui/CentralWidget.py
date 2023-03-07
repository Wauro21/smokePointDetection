import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from Plot.FixedPlots import FixedPlot, PolyHeightPlot
from Plot.CentroidPlot import CentroidPlotWidget
from LoadWidget import LoadWidget
from Frameplayer.VideoPlayer import FrameHolder
from Plot.ProcessPlot import ProcessPlotWidget
from GUI_CONSTANTS import CentroidTypes, FrameTypes, InformationStatus
from Plot.PlotHolder import PlotHolder
from Preprocessing.CutWidget import CutWidget
from Preprocessing.Preprocessing import PreprocessingWidget
from Preprocessing.ThresholdWidget import ThresholdWidget
from Preprocessing.InfoWidget import DisplaySettings
from RunInformation import InformationBar, InformationTab
from MessageBox import WarningBox
from Thread import PloyAnalizer
__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'

class CentralWidget(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)

        # Objects 
        self.video_path = None
        self.demo_frame_path = None
        self.polyThread = None

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
            'n_invalid_frames': 0,
            'centroid_ref_cord': None, 
            'last_run_time': 0,
            '10th_poly': None,
            '10th_der': None, 
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
        self.PolyHeightPlot = PolyHeightPlot('h v/s H')
        self.Plotholder = PlotHolder([self.HeightPlot, self.CentroidPlot, self.PolyHeightPlot],self)

        # -> Information bar
        self.infoBar = InformationBar(self)
        self.infoTab = InformationTab(self)

        # Init routines
        self.PreprocessingTabs.addTab(self.CutWindow, 'Cut frame', True)
        self.PreprocessingTabs.addTab(self.ThresholdWindow, 'Threshold controls', False)
        self.PreprocessingTabs.addTab(self.DisplayWindow, 'Run settings', False)
        self.DisplayWindow.applyHandler(self.enableStart)
        self.LoadWidget.startHandler(self.requestStart)
        self.Plotholder.addTab(self.infoTab)

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

    def plotHeightsPoly(self):
        self.PolyHeightPlot.plot(self.process_controls)

    def requestPolynomialAnalysis(self):
        if(self.polyThread != None):
            warning = WarningBox('There is already a thread performing the analysis, wait until it finishes before attempting to perform the analysis again.')
            warning.exec_()
            return False
        
        self.polyThread = PloyAnalizer(self.process_controls)
        self.polyThread.heights_plot.connect(self.plotHeightsPoly)
        self.polyThread.start()


    def frameProcessDone(self):
        # Change status
        self.infoBar.setStatus(InformationStatus.FRAMES_DONE)
        # Get last run time
        self.process_controls['last_run_time'] = self.infoBar.getLastTime()
        # Update info summary
        self.infoTab.updateTabs(self.process_controls)

        # Set current tab 
        self.Plotholder.setCurrentTab(2)

        # REMOVE LATER ONLY TEMPORAL
        self.requestPolynomialAnalysis()

    def centroidSignalHandler(self, message):
        # Update centroid plot
        self.CentroidPlot.update(message)
        self.infoBar.stepBar(self.process_controls['n_frames'])

        # If reference set it to the info
        message_type = list(message.keys())[-1]
        if(message_type is CentroidTypes.REFERENCE):
            self.process_controls['centroid_ref_cord'] = message[message_type]

        # Updat invalid counter
        if(message_type is CentroidTypes.INVALID):
            self.process_controls['n_invalid_frames'] += 1

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