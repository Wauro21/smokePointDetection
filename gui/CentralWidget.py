import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from Plot.FixedPlots import FixedPlot, LinearRegionPlot, PolyHeightPlot, SmokePointPlot
from Plot.CentroidPlot import CentroidPlotWidget
from LoadWidget import LoadWidget
from Frameplayer.VideoPlayer import FrameHolder
from Plot.ProcessPlot import ProcessPlotWidget
from GUI_CONSTANTS import CentroidTypes, FrameTypes, InformationStatus, StartStates
from TabHolder import TabHolder
from Preprocessing.CutWidget import CutWidget
from Preprocessing.Preprocessing import PreprocessingWidget
from Preprocessing.ThresholdWidget import ThresholdWidget
from Preprocessing.InfoWidget import DisplaySettings
from RunInformation import InformationBar, InformationTab
from MessageBox import WarningBox
from Thread import PolyAnalizer
from Preprocessing.CameraCalibration import CameraCalibration
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
        self.process_controls = {}
        # Init the controls
        self.clearControls()


        # Widgets
        self.LoadWidget = LoadWidget(self.process_controls, self)
        self.VideoWidget = FrameHolder(self.process_controls, self)
        # -> Preprocess : No parent so can be displayed as new window
        self.PreprocessingTabs = PreprocessingWidget()
        self.CutWindow = CutWidget(self.process_controls, self.PreprocessingTabs)
        self.ThresholdWindow = ThresholdWidget(self.process_controls, self.PreprocessingTabs)
        self.DisplayWindow = DisplaySettings(self.process_controls, self.PreprocessingTabs)
        self.CameraCalibration = CameraCalibration(self.process_controls, self.PreprocessingTabs)
        self.TabHolder = TabHolder(self)

        # -> Plots 
        self.HeightPlot = ProcessPlotWidget(self)
        self.CentroidPlot = CentroidPlotWidget(self)
        self.PolyHeightPlot = PolyHeightPlot(self)
        self.LinearPolyPlot = LinearRegionPlot(self)
        self.SmokePointPlot = SmokePointPlot(self)

        # -> Information bar
        self.infoBar = InformationBar(self)
        self.infoTab = InformationTab(self)

        # Init routines
        self.PreprocessingTabs.addTab(self.CutWindow, True)
        self.PreprocessingTabs.addTab(self.ThresholdWindow, False)
        self.PreprocessingTabs.addTab(self.CameraCalibration, True)
        self.PreprocessingTabs.addTab(self.DisplayWindow, False)
        self.DisplayWindow.applyHandler(self.enableStart)
        
        # -> Add tabs to tab holder 
        self.TabHolder.addTab(self.HeightPlot)
        self.TabHolder.addTab(self.CentroidPlot)
        self.TabHolder.addTab(self.PolyHeightPlot, False)
        self.TabHolder.addTab(self.LinearPolyPlot, False)
        self.TabHolder.addTab(self.SmokePointPlot, False, True)
        self.TabHolder.addTab(self.infoTab)

        # Signals and Slots
        self.LoadWidget.path_signal.connect(self.setPrefix)
        self.LoadWidget.configureHandler(self.requestCutting)
        self.LoadWidget.start.connect(self.requestStart)
        self.LoadWidget.stop.connect(self.requestStop)
        self.CutWindow.preprocess_done.connect(self.requestThreshold)
        self.ThresholdWindow.done_signal.connect(self.requestDisplay)
        self.VideoWidget.frame_process_done.connect(self.frameProcessDone)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.LoadWidget)

        # -> Video and plot area
        video_plot_layout = QHBoxLayout()
        video_plot_layout.addWidget(self.VideoWidget)
        video_plot_layout.addWidget(self.TabHolder)
        layout.addLayout(video_plot_layout)

        layout.addWidget(self.infoBar)
        
        self.setLayout(layout)


    def requestStop(self):
        self.process_controls['stop'] = True

    def stopClean(self):
        # Clean the plots
        self.HeightPlot.clearPlot()
        self.CentroidPlot.clearPlot()

        # Update start button status
        self.LoadWidget.externalStartButton(StartStates.ENABLED)

        # Restore stop flag
        self.process_controls['stop'] = False


    def clearPreviousRun(self):
        # Clean process results stored
        self.process_controls['h'] = None
        self.process_controls['H'] = None
        self.process_controls['n_invalid_frames'] = 0
        self.process_controls['centroid_ref_cord'] = None
        self.process_controls['last_frame_run'] = 0
        self.process_controls['10th_poly'] = None
        self.process_controls['10th_der'] = None
        self.process_controls['der_threshold'] : 1e-2 # REMOVE
        self.process_controls['linear_region'] = None
        self.process_controls['linear_poly'] = None
        self.process_controls['sp'] = None
        self.process_controls['last_poly_run'] = 0

        # Clean the info tabs
        self.infoTab.clearTabs()

    def clearControls(self):
        self.process_controls = {
            'stop': False,
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
            'last_frame_run': 0,
            '10th_poly': None,
            '10th_der': None, 
            'der_threshold': 1e-2, # Temporal
            'linear_region': None,
            'linear_poly': None,
            'sp': None,
            'last_poly_run': 0,
        }


    def plotSmokePoint(self):
        self.SmokePointPlot.plot(self.process_controls)

    def plotLinearPoly(self):
        self.LinearPolyPlot.plot(self.process_controls)

    def plotHeightsPoly(self):
        self.PolyHeightPlot.plot(self.process_controls)

    def polynomialAnalysisDone(self):
        # Stop timer
        self.infoBar.setStatus(InformationStatus.DONE)
        # Get last run for poly
        self.process_controls['last_poly_run'] = self.infoBar.getLastTime()
        
        # Clean thread
        self.polyThread = None

        # Show invisibles plots
        self.TabHolder.toggleInvinsibles()

        # Update information
        self.infoTab.updatePolyTab(self.process_controls)

        # Update start button status
        self.LoadWidget.externalStartButton(StartStates.ENABLED)


    def requestPolynomialAnalysis(self):
        if(self.polyThread != None):
            warning = WarningBox('There is already a thread performing the analysis, wait until it finishes before attempting to perform the analysis again.')
            warning.exec_()
            return False
        
        self.polyThread = PolyAnalizer(self.process_controls)
        self.polyThread.heights_plot.connect(self.plotHeightsPoly)
        self.polyThread.linear_plot.connect(self.plotLinearPoly)
        self.polyThread.linear_error.connect(lambda: print('ERROR on linear region'))
        self.polyThread.sp_plot.connect(self.plotSmokePoint)
        self.polyThread.finished.connect(self.polynomialAnalysisDone)
        self.polyThread.started.connect(lambda: self.infoBar.setStatus(InformationStatus.POLYNOMIAL))
        self.polyThread.start()


    def frameProcessDone(self):
        if(self.process_controls['stop']):
            self.stopClean()
            return False
        
        # Change status
        self.infoBar.setStatus(InformationStatus.FRAMES_DONE)
        # Get last run time
        self.process_controls['last_frame_run'] = self.infoBar.getLastTime()
        # Update info summary
        self.infoTab.updateFrameTab(self.process_controls)

        # Set current tab 
        self.TabHolder.showResultTab() 

        self.requestPolynomialAnalysis()

        return True

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
        self.LoadWidget.externalStartButton(StartStates.ENABLED)

    def requestDisplay(self):
        # Update run settings display
        self.DisplayWindow.updateInfo()
        self.PreprocessingTabs.setTabEnabled(2, True)
        self.PreprocessingTabs.setCurrentIndex(2)

    def requestStart(self):
        # Clear older runs
        self.clearPreviousRun()
        # Handle the info bar display and timer
        self.infoBar.setStatus(InformationStatus.FRAMES)
        # Handle the start button status
        self.LoadWidget.externalStartButton(StartStates.STOP)
        # Start the thread for video playback
        self.VideoWidget.startPlayback(self.video_path, self.HeightPlot.update, self.centroidSignalHandler)

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



if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = CentralWidget()
    widget.show()
    sys.exit(app.exec_())