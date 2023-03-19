from datetime import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QProgressBar, QGroupBox
from PyQt5 import QtCore
from gui.GUI_CONSTANTS import INFORMATION_BAR_ELAPSED_FIELD, INFORMATION_BAR_ELAPSED_LABEL, INFORMATION_BAR_OPERATION_LABEL, INFORMATION_LABELS_WIDTH, INFORMATION_POLYNOMIAL_CONV_FACTOR,INFORMATION_POLYNOMIAL_N_POINT_LINEAR_REGION, INFORMATION_POLYNOMIAL_PLACEHOLDER, INFORMATION_POLYNOMIAL_PROCESSING_TIME, INFORMATION_POLYNOMIAL_SP_MM_VALUE, INFORMATION_POLYNOMIAL_SP_MM_VALUE_FIELD, INFORMATION_POLYNOMIAL_SP_VALUE_FIELD, INFORMATION_POLYNOMIAL_SP_VALUE_FOUND, INFORMATION_POLYNOMIAL_TAB_TITLE, INFORMATION_POLYNOMIAL_THRESHOLD_VALUE, INFORMATION_PROCESSED_CENTROID_DECIMALS, INFORMATION_PROCESSED_CENTROID_LABEL, INFORMATION_PROCESSED_CONTOUR_LABEL, INFORMATION_PROCESSED_CORE_LABEL, INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, INFORMATION_PROCESSED_ROW_CENTROID, INFORMATION_PROCESSED_ROW_H_POINTS, INFORMATION_PROCESSED_ROW_INVALID_FRAMES, INFORMATION_PROCESSED_ROW_NUMBER_FRAMES, INFORMATION_PROCESSED_ROW_TIME, INFORMATION_PROCESSED_ROW_TIP_POINTS, INFORMATION_PROCESSED_TAB_TITLE, INFORMATION_PROCESSED_THRESHOLD_FIELD, INFORMATION_TAB_DISPLAY_HEIGHT, INFORMATION_TAB_DISPLAY_WIDTH, PLOT_WIDGET_WIDTH, InformationStatus
from PyQt5.QtCore import QTimer


class InformationTab(QWidget):

    def __init__(self, process_controls, parent=None):
        super().__init__(parent)

        # Objects
        self.process_controls = process_controls
        self.title = 'Process Summary'


        # Widgets
        self.frame_info = FrameInformation(self)
        self.poly_info = PolynomialInformation(self)

        # Init 

        
        # Signals and Slots


        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.frame_info)
        layout.addWidget(self.poly_info)

        self.setLayout(layout)

    def updateFrameTab(self, process_controls):
        self.frame_info.updateInformation(process_controls)

    def updatePolyTab(self, process_controls):
        self.poly_info.updateInformation(process_controls)

    def updateTabs(self, process_controls):
        self.frame_info.updateInformation(process_controls)
        self.poly_info.updateInformation(process_controls)

    def getTitle(self):
        return self.title
    
    def clearTabs(self):
        self.frame_info.clearInformation()
        self.poly_info.clearInformation()
    
class PolynomialInformation(QWidget):

    def __init__(self, parent=None):
        
        super().__init__(parent)

        # Objects

        # Widgets
        group = QGroupBox(INFORMATION_POLYNOMIAL_TAB_TITLE, self)
        self.n_points_linear = QLabel(INFORMATION_POLYNOMIAL_PLACEHOLDER, self)
        self.der_threshold = QLabel(INFORMATION_POLYNOMIAL_PLACEHOLDER, self)
        self.sp_value = QLabel(INFORMATION_POLYNOMIAL_PLACEHOLDER, self)
        self.processing_time = QLabel(INFORMATION_POLYNOMIAL_PLACEHOLDER, self)
        self.conv_factor = QLabel(INFORMATION_POLYNOMIAL_PLACEHOLDER, self)
        self.sp_mm = QLabel(INFORMATION_POLYNOMIAL_PLACEHOLDER, self)
        self.labels = [self.n_points_linear, self.der_threshold, self.sp_value, self.processing_time, self.conv_factor, self.sp_mm]
        
        # init routines
        self.setFixedWidth(INFORMATION_TAB_DISPLAY_WIDTH)
        self.setFixedHeight(INFORMATION_TAB_DISPLAY_HEIGHT)
        group.setStyleSheet('QGroupBox { font-weight: bold;}')

        for label in self.labels:
            label.setStyleSheet(
                'margin-left:20px;'
            )
            label.setAlignment(QtCore.Qt.AlignRight)


        # Signals and Slots

        # Layout
        layout = QVBoxLayout()

        # -> Info display
        display = QHBoxLayout()

        # -> Left display
        info_left = QFormLayout()
        info_left.addRow(INFORMATION_POLYNOMIAL_THRESHOLD_VALUE, self.der_threshold)
        info_left.addRow(INFORMATION_POLYNOMIAL_SP_VALUE_FOUND, self.sp_value)
        info_left.addRow(INFORMATION_POLYNOMIAL_CONV_FACTOR, self.conv_factor)

        # -> Right display
        info_right = QFormLayout()
        info_right.addRow(INFORMATION_POLYNOMIAL_N_POINT_LINEAR_REGION, self.n_points_linear)
        info_right.addRow(INFORMATION_POLYNOMIAL_PROCESSING_TIME, self.processing_time)
        info_right.addRow(INFORMATION_POLYNOMIAL_SP_MM_VALUE, self.sp_mm)

        display.addLayout(info_left)
        display.addLayout(info_right)

        group.setLayout(display)
        layout.addWidget(group)

        self.setLayout(layout)

    def updateInformation(self, process_controls):
        der_threshold = str(process_controls['controls']['der_threshold'])
        n_points = process_controls['results']['linear_region']
        n_points_linear = INFORMATION_POLYNOMIAL_PLACEHOLDER
        if(n_points):
            n_points_linear = str(len(n_points))
        
        sp_info = process_controls['results']['sp']
        sp_value = INFORMATION_POLYNOMIAL_PLACEHOLDER
        sp_value_mm = INFORMATION_POLYNOMIAL_PLACEHOLDER
        if(sp_info):
            sp_value = INFORMATION_POLYNOMIAL_SP_VALUE_FIELD.format(sp_info[0]) # Only contour height
            in_mm = sp_info[0]*process_controls['controls']['conv_factor']
            sp_value_mm = INFORMATION_POLYNOMIAL_SP_MM_VALUE_FIELD.format(in_mm)
            
        conv_factor = str(process_controls['controls']['conv_factor'])
        processing_time = str(process_controls['results']['last_poly_run'])

        self.der_threshold.setText(der_threshold)
        self.n_points_linear.setText(n_points_linear)
        self.sp_value.setText(sp_value)
        self.processing_time.setText(processing_time)
        self.sp_mm.setText(sp_value_mm)
        self.conv_factor.setText(conv_factor)

    def clearInformation(self):
        for label in self.labels:
            label.setText(INFORMATION_POLYNOMIAL_PLACEHOLDER)






class FrameInformation(QWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)

        # Objects

        # Widgets
        group = QGroupBox(INFORMATION_PROCESSED_TAB_TITLE,self)
        self.core = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.contour = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.n_frames = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.n_invalid_frames = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.centroid_reference = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.n_points_h = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.n_points_H = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.processing_time = QLabel(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER, group)
        self.labels = [self.n_frames, self.n_invalid_frames, self.centroid_reference, self.n_points_h, self.n_points_H, self.processing_time, self.core, self.contour]

        # init routines
        self.setFixedWidth(INFORMATION_TAB_DISPLAY_WIDTH)
        self.setFixedHeight(INFORMATION_TAB_DISPLAY_HEIGHT)
        group.setStyleSheet('QGroupBox { font-weight: bold;}')

        for label in self.labels:
            label.setStyleSheet(
                'margin-left:20px;'
            )
            label.setAlignment(QtCore.Qt.AlignRight)

        # Signals and Slots

        # Layout
        layout = QVBoxLayout()

        # -> info display
        display = QHBoxLayout()
        
        info_left = QFormLayout()
        info_left.addRow(INFORMATION_PROCESSED_CORE_LABEL, self.core)
        info_left.addRow(INFORMATION_PROCESSED_ROW_NUMBER_FRAMES, self.n_frames)
        info_left.addRow(INFORMATION_PROCESSED_ROW_INVALID_FRAMES, self.n_invalid_frames)
        info_left.addRow(INFORMATION_PROCESSED_ROW_H_POINTS, self.n_points_h)
        display.addLayout(info_left)

        info_right = QFormLayout()
        info_right.addRow(INFORMATION_PROCESSED_CONTOUR_LABEL, self.contour)
        info_right.addRow(INFORMATION_PROCESSED_ROW_TIME, self.processing_time)
        info_right.addRow(INFORMATION_PROCESSED_ROW_CENTROID, self.centroid_reference)
        info_right.addRow(INFORMATION_PROCESSED_ROW_TIP_POINTS, self.n_points_H)
        display.addLayout(info_right)


        group.setLayout(display)
        layout.addWidget(group)

        self.setLayout(layout)

    def updateInformation(self, process_controls):
        core = INFORMATION_PROCESSED_THRESHOLD_FIELD.format(process_controls['controls']['core_%'])
        contour = INFORMATION_PROCESSED_THRESHOLD_FIELD.format(process_controls['controls']['contour_%'])
        n_frames = str(process_controls['frames_info']['n_frames'])
        n_invalid_frames = str(process_controls['results']['n_invalid_frames'])
        centroid = str(round(process_controls['results']['centroid_ref_cord'], INFORMATION_PROCESSED_CENTROID_DECIMALS))
        last_time = str(process_controls['results']['last_frame_run'])
        h_points = str(len(process_controls['results']['h']))
        H_points = str(len(process_controls['results']['H']))

        self.core.setText(core)
        self.contour.setText(contour)
        self.n_frames.setText(n_frames)
        self.n_invalid_frames.setText(n_invalid_frames)
        self.centroid_reference.setText(INFORMATION_PROCESSED_CENTROID_LABEL.format(centroid))
        self.processing_time.setText(last_time)
        self.n_points_h.setText(h_points)
        self.n_points_H.setText(H_points)

    def clearInformation(self):
        for label in self.labels:
            label.setText(INFORMATION_PROCESSED_FRAMES_PLACEHOLDER)


class InformationBar(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)

        # Objects
        self.status = None
        self.last_steps = None
        self.start_time = None
        self.last_run = None

        # Widgets
        self.operation_label = QLabel(INFORMATION_BAR_OPERATION_LABEL, self)
        self.operation_field = QLabel(InformationStatus.IDLE.value, self)
        self.elapsed_label = QLabel(INFORMATION_BAR_ELAPSED_LABEL, self)
        self.elapsed_field = QLabel(INFORMATION_BAR_ELAPSED_FIELD.format(0,0,0), self)
        self.elapsed_time = QTimer(self)
        self.progress = QProgressBar(self)

        # init routines
        self.elapsed_time.setInterval(1000) # Change to setInterval

        self.operation_label.setStyleSheet(
            'font-weight: bold'
        )

        self.elapsed_label.setStyleSheet(
            'font-weight: bold'
        )

        self.progress.setFixedWidth(PLOT_WIDGET_WIDTH)
        self.operation_label.setFixedWidth(INFORMATION_LABELS_WIDTH)
        self.operation_field.setFixedWidth(INFORMATION_LABELS_WIDTH)
        self.elapsed_label.setFixedWidth(INFORMATION_LABELS_WIDTH)
        self.operation_field.setFixedWidth(INFORMATION_LABELS_WIDTH)

        # Slots and Signals
        self.elapsed_time.timeout.connect(self.updateTime)

        # Layout
        layout = QHBoxLayout()
        layout.addStretch(1)
        # -> Information
        info = QFormLayout()
        info.addRow(self.operation_label, self.operation_field)
        info.addRow(self.elapsed_label, self.elapsed_field)

        layout.addLayout(info)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def setStatus(self, status):
        self.status = status
        self.operation_field.setText(self.status.value)
        if(self.status is InformationStatus.FRAMES or self.status is InformationStatus.POLYNOMIAL):
            # Start elapsed time 
            self.start()

        if(self.status is InformationStatus.FRAMES_DONE or self.status is InformationStatus.POLYNOMIAL):
            # Restart the timer
            self.restart()


    def restart(self):
        self.last_run = self.elapsed_field.text()
        self.start_time = None
        self.elapsed_time.stop()
        self.setTimeLabel(0, 0, 0)

    def start(self):
        self.last_steps = 0
        self.start_time = datetime.now()
        self.elapsed_time.start()

    def updateTime(self):
        # Get current time 
        time = datetime.now()
        # Calculate elapsed
        elapsed = time -self.start_time
        sec = elapsed.seconds
        disp_sec = sec%60
        hours = sec // 3600
        minutes = (sec // 60) - (hours*60)
        self.setTimeLabel(hours, minutes, disp_sec)
        
    def setTimeLabel(self, hours, minutes, secs):
        time_string = INFORMATION_BAR_ELAPSED_FIELD.format(hours, minutes, secs)
        self.elapsed_field.setText(time_string)
        

    def stepBar(self, total):
        self.last_steps += 1
        value = round(100*(self.last_steps/total))
        self.progress.setValue(value)

    def getLastTime(self):
        return self.last_run