import sys
import json
import os
import datetime
from PyQt5.QtWidgets import QFileDialog, QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from Plot.FixedPlots import FixedPlot, LinearRegionPlot, PolyHeightPlot, SmokePointPlot
from Plot.CentroidPlot import CentroidPlotWidget
from LoadWidget import LoadWidget
from Frameplayer.VideoPlayer import FrameHolder
from Plot.ProcessPlot import ProcessPlotWidget
from GUI_CONSTANTS import PREPROCESSING_CAMERA_CALIBRATION_SAVE_DESC, PREPROCESSING_CAMERA_CALIBRATION_SAVE_TITLE, CentroidTypes, FrameTypes, InformationStatus, StartStates
from TabHolder import TabHolder
from Preprocessing.CutWidget import CutWidget
from Preprocessing.Preprocessing import PreprocessingWidget
from Preprocessing.ThresholdWidget import ThresholdWidget
from Preprocessing.InfoWidget import DisplaySettings
from RunInformation import InformationBar, InformationTab
from MessageBox import ErrorBox, WarningBox
from Thread import PolyAnalizer
from Preprocessing.CameraCalibration import CameraCalibration
from CONSTANTS import DERIVATIVE_LOW_BOUND, MAX_CENTROID_TOLERANCE
__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'

class CentralWidget(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)

        # Objects 
        self.video_path = None
        self.demo_frame_path = None
        self.polyThread = None
        self.preprocessing_tab_index = []
        self.autocut = True
        self.invisibles_idx = {}

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
        self.CentroidPlot = CentroidPlotWidget(self.process_controls,self)
        self.PolyHeightPlot = PolyHeightPlot(self)
        self.LinearPolyPlot = LinearRegionPlot(self)
        self.SmokePointPlot = SmokePointPlot(self)

        # -> Information bar
        self.infoBar = InformationBar(self)
        self.infoTab = InformationTab(self)

        # Init routines
        self.preprocessing_tab_index.append(self.PreprocessingTabs.addTab(self.CutWindow, True))
        self.preprocessing_tab_index.append(self.PreprocessingTabs.addTab(self.ThresholdWindow, False))
        self.preprocessing_tab_index.append(self.PreprocessingTabs.addTab(self.CameraCalibration, False))
        self.preprocessing_tab_index.append(self.PreprocessingTabs.addTab(self.DisplayWindow, False))
        self.DisplayWindow.applyHandler(self.enableStart)
        
        # -> Add tabs to tab holder 
        self.TabHolder.addTab(self.HeightPlot)
        self.TabHolder.addTab(self.CentroidPlot)
        self.invisibles_idx['poly'] = self.TabHolder.addTab(self.PolyHeightPlot, False)
        self.invisibles_idx['linear'] = self.TabHolder.addTab(self.LinearPolyPlot, False)
        self.invisibles_idx['poly'] = self.TabHolder.addTab(self.SmokePointPlot, False, True)
        self.TabHolder.addTab(self.infoTab)

        # Signals and Slots
        self.LoadWidget.path_signal.connect(self.setPrefix)
        self.LoadWidget.configureHandler(self.requestCutting)
        self.LoadWidget.start.connect(self.requestStart)
        self.LoadWidget.stop.connect(self.requestStop)
        self.LoadWidget.load_config.connect(self.updatePreprocessing)
        self.CutWindow.preprocess_done.connect(self.requestThreshold)
        self.ThresholdWindow.done_signal.connect(self.requestCalibration)
        self.CameraCalibration.calibration_done.connect(self.requestDisplay)
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

    def linearError(self):
        self.process_controls['signals']['linear_error'] = True
        message = ErrorBox('The selected derivative threshold ({}) resulted in a linear region with less than two points. Try with another threshold!'.format(self.process_controls['controls']['der_threshold']))
        message.exec_()

    def spError(self):
        self.process_controls['signals']['sp_error'] = True
        message = WarningBox('The sp could not be found with the provided settings!')
        message.exec_()

    def clearPlots(self):
        self.HeightPlot.clearPlot()
        self.CentroidPlot.clearPlot()
        self.PolyHeightPlot.clearPlot()
        self.LinearPolyPlot.clearPlot()
        self.SmokePointPlot.clearPlot()

    def updatePreprocessing(self):
        # Enable all tabs
        for tab in self.preprocessing_tab_index:
            self.PreprocessingTabs.setTabEnabled(tab, True)

        # Force update
        # -> cutWidget
        self.autocut=False
        self.CutWindow.setFrame(self.demo_frame_path, autocut=False)
        self.CutWindow.forceUpdate()

        # -> threshold widget
        self.ThresholdWindow.setFrame(self.demo_frame_path)
        self.ThresholdWindow.forceUpdate()

        # -> Camera widget
        self.CameraCalibration.forceUpdate()

        # -> info widget
        self.DisplayWindow.forceUpdate()


    def requestStop(self):
        self.process_controls['signals']['stop'] = True

    def stopClean(self):
        # Clean the plots
        self.HeightPlot.clearPlot()
        self.CentroidPlot.clearPlot()

        # Update start button status
        self.LoadWidget.externalStartButton(StartStates.ENABLED)

        # Restore stop flag
        self.process_controls['signals']['stop'] = False


    def clearPreviousRun(self):
        # Clean previous results
        self.process_controls['results']['h'] = None
        self.process_controls['results']['H'] = None
        self.process_controls['results']['n_invalid_frames'] = 0
        self.process_controls['results']['centroid_ref_cord'] = None
        self.process_controls['results']['last_frame_run'] = 0
        self.process_controls['results']['10th_poly'] = None
        self.process_controls['results']['10th_der'] = None
        self.process_controls['results']['linear_region'] = None
        self.process_controls['results']['linear_poly'] = None
        self.process_controls['results']['sp'] = None
        self.process_controls['results']['last_poly_run'] = 0

        # Clean the info tabs
        self.infoTab.clearTabs()

    def clearControls(self):

        self.process_controls = {
            # Main controls of the process
            'controls': {
                'core_%': 0,
                'contour_%': 0,
                'cut': None,
                'conv_factor': 0,
                'der_threshold': DERIVATIVE_LOW_BOUND,
                'centroid_tol': MAX_CENTROID_TOLERANCE,
            },

            # Info about the loaded media
            'frames_info':{
                'n_frames': 0,
                'bboxes': False,
                'centroids': False,
                'display': FrameTypes.FRAME,
            },

            # Signal vector
            'signals':{
                'stop': False,
                'linear_error': False,
                'sp_error': False,
            },

            # Results
            'results':{
                'n_frames': 0,
                'h': None,
                'H': None,
                'n_invalid_frames': 0,
                'centroid_ref_cord': None, 
                'last_frame_run': 0,
                '10th_poly': None,
                '10th_der': None,
                'linear_region': None,
                'linear_poly': None,
                'sp': None,
                'last_poly_run': 0,
            }
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
        self.process_controls['results']['last_poly_run'] = self.infoBar.getLastTime()
        
        # Clean thread
        self.polyThread = None

        if(self.process_controls['signals']['linear_error']):
            # Only show the poly plot
            self.TabHolder.setVisible(self.invisibles_idx['poly'])

        elif(self.process_controls['signals']['sp_error']):
            # Show poly and linear region
            self.TabHolder.setVisible(self.invisibles_idx['poly'])
            self.TabHolder.setVisible(self.invisibles_idx['linear'])

        else:
            # Show invisibles plots
            self.TabHolder.toggleInvinsibles()

        
        # Update information
        self.infoTab.updatePolyTab(self.process_controls)

        # Update start button status and unlock buttons
        self.LoadWidget.lockUserControls(True)
        self.LoadWidget.externalStartButton(StartStates.ENABLED)


    def requestPolynomialAnalysis(self):
        if(self.polyThread != None):
            warning = WarningBox('There is already a thread performing the analysis, wait until it finishes before attempting to perform the analysis again.')
            warning.exec_()
            return False
        
        self.polyThread = PolyAnalizer(self.process_controls)
        self.polyThread.heights_plot.connect(self.plotHeightsPoly)
        self.polyThread.linear_plot.connect(self.plotLinearPoly)
        self.polyThread.sp_plot.connect(self.plotSmokePoint)
        self.polyThread.finished.connect(self.polynomialAnalysisDone)
        self.polyThread.started.connect(lambda: self.infoBar.setStatus(InformationStatus.POLYNOMIAL))
        self.polyThread.linear_error.connect(self.linearError)
        self.polyThread.sp_error.connect(self.spError)
        self.polyThread.start()


    def frameProcessDone(self):
        stop = self.process_controls['signals']['stop']
        if(stop):
            self.stopClean()
            return False
        
        # Change status
        self.infoBar.setStatus(InformationStatus.FRAMES_DONE)
        # Get last run time
        self.process_controls['results']['last_frame_run'] = self.infoBar.getLastTime()
        # Update info summary
        self.infoTab.updateFrameTab(self.process_controls)

        # Set current tab 
        self.TabHolder.showResultTab() 

        self.requestPolynomialAnalysis()

        return True

    def centroidSignalHandler(self, message):
        # Update centroid plot
        self.CentroidPlot.update(message)
        self.infoBar.stepBar(self.process_controls['frames_info']['n_frames'])

        # If reference set it to the info
        message_type = list(message.keys())[-1]
        if(message_type is CentroidTypes.REFERENCE):
            self.process_controls['results']['centroid_ref_cord'] = message[message_type]

        # Updat invalid counter
        if(message_type is CentroidTypes.INVALID):
            self.process_controls['results']['n_invalid_frames'] += 1

    def enableStart(self):
        self.PreprocessingTabs.requestClose()
        self.LoadWidget.externalStartButton(StartStates.ENABLED)

    def requestCalibration(self):
        self.DisplayWindow.updateInfo()
        self.PreprocessingTabs.setTabEnabled(2, True)
        self.PreprocessingTabs.setCurrentIndex(2)

    def requestDisplay(self):
        # Update run settings display
        self.DisplayWindow.updateInfo()
        self.PreprocessingTabs.setTabEnabled(3, True)
        self.PreprocessingTabs.setCurrentIndex(3)

    def requestStart(self):
        # Clear older runs
        self.clearPreviousRun()

        # Hide old result plots and set visible tab to first one 
        self.TabHolder.setInvisibles(False)
        self.TabHolder.setCurrentTab(0)

        # Clear plots 
        self.clearPlots()
        # Handle the info bar display and timer
        self.infoBar.setStatus(InformationStatus.FRAMES)
        # Handle the start button status and lock user controls
        self.LoadWidget.lockUserControls(False)
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
        self.CutWindow.setFrame(self.demo_frame_path, self.autocut)
        #self.ThresholdWindow.setFrame(self.demo_frame_path)
        self.PreprocessingTabs.show()

    def updateCutInfo(self):
        self.process_controls['controls']['cut'] = self.LoadWidget.getCutInfo()

    def setPrefix(self, values):
        self.video_path, self.demo_frame_path = values



if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = CentralWidget()
    widget.show()
    sys.exit(app.exec_())