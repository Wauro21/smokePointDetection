from enum import Enum

# Colors
GUI_RED_ERROR_BG = '#f86e6c'

# LoadWdiget

# -> Display message for QLineEdit used for file selection
LOAD_WIDGET_FILE_DEFAULT_MESSAGE = 'Select a frame folder to process'
LOAD_WIDGET_FILE_DIALOG_HEADER_TITLE = 'Select a folder to process'
LOAD_WIDGET_LOAD_JSON = 'Load settings from file'

# -> Start button states
class StartStates(Enum):
    LOCKED = 0
    ENABLED = 1
    STOP = 2

LOAD_START_BUTTON_ENABLED_TEXT = 'Start'
LOAD_START_BUTTON_STOP_TEXT = 'Stop'

# VideoPlayer

VIDEO_PLAYER_BG_COLOR = '#303539'
VIDEO_PLAYER_BG_COLOR_BGR = (22, 21, 19)
VIDEO_PLAYER_BG_COLOR_GRAY = 255 # To define
VIDEO_PLAYER_HEIGHT_DEFAULT = 480
VIDEO_PLAYER_WIDTH_DEFAULT = 200

# Type of frames to display
class FrameTypes(Enum):
    FRAME = 0
    GRAY = 1
    CORE = 2
    CONTOUR = 3
    CORE_CC = 4
    CONTOUR_CC = 5


# Mouse event offset 
# -> To feel more natural when selecting the area of interest offset 
MOUSE_EVENT_PIXEL_OFFSET = 32


# Preprocessing
PREPROCESSING_MAIN_DESCRIPTION = 'Narrow the area of interest to remove redundant frame information. Then select the threshold values for the areas of interest to start the process.'
PREPROCESSING_MINIMUM_WIDTH = 100#
PREPROCESSING_SCROLL_WIDTH_STEP = 10
PREPROCESSING_WINDOW_TITLE = 'Preprocessing'
PREPROCESSING_TITLE_MESSAGE= 'Select the region of interest to cut the frames and save processing time'
PREPROCESSING_DESC_MESSAGE = 'Left click on the approximate center of the flame and adjust the width of the region, scrolling the mouse wheel. You can use the controls to fine tune the area. You can also save/load this presets for future use.'

PREPROCESSING_CUT_WIDGET_TAB_TITLE = 'Cut Frame'
PREPROCESSING_THRESHOLD_WIDGET_TAB_TITLE = 'Threshold controls'
PREPROCESSING_DISPLAY_WIDGET_TAB_TITLE = 'Run settings'
PREPROCESSING_CAMERA_CALIBRATION_WIDGET_TAB_TITLE='Camera Calibration'

# -> Camera calibration 
PREPROCESSING_CAMERA_CALIBRATION_LOAD_IMAGE = 'Select a chessboard image'
PREPROCESSING_CAMERA_CALIBRATION_LOAD_DIALOG = 'Select a chessboard image'
PREPROCESSING_CAMERA_CALIBRATION_PLOT_FRAME_TITLE = 'Calibration Image'
PREPROCESSING_CAMERA_CALIBRATION_THRESHOLD_FRAME_TITLE = 'Threshold Image'
PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_TITLE = 'Camera Calibration:'
PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_DESC = 'Allows to get the convertion from pixels to milimiters. This is done by automatically analyzing a chessboard image of the experimental setup.'
PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARES = 'N° of squares on chessboard:'
PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_SQUARE_SIDE = 'Square side:'
PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG = 'Square side AVG:'
PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_AVG_FIELD = '{:.2f} px'
PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD = 'Square side STD:'
PREPROCESSING_CAMERA_CALIBRATION_CONTROLS_PX_STD_FIELD = '{:.2f} px'
PREPROCESSING_CAMERA_CALIBRATION_PX_MM_TITLE = 'Conversion factor:'
PREPROCESSING_CAMERA_CALIBRATION_PX_MM_DESC = 'Val_mm = Val_px * (square_side_mm / square_side_px)'
PREPROCESSING_CAMERA_CALIBRATION_PX_MM_A_LABEL = 'Factor:'
PREPROCESSING_CAMERA_CALIBRATION_CORNER_COLOR = '#F48815'
PREPROCESSING_CAMERA_CALIBRATION_MIN_SQUARES = 5
PREPROCESSING_CAMERA_CALIBRATION_MIN_SQUARE_SIDE = 1 #mm
PREPROCESSING_CAMERA_CALIBRATION_NO_CORNERS_ERROR = 'No squares could be found on the image, try checking the input fields and chessboard image!'
PREPROCESSING_CAMERA_CALIBRATION_SQUARE_SIDE_UNIT = '  mm'
PREPROCESSING_CAMERA_CALIBRATION_FACTOR = '  mm/px'
PREPROCESSING_CAMERA_CALIBRATION_SAVE_TITLE = 'Save the calibration factor to a file'
PREPROCESSING_CAMERA_CALIBRATION_SAVE_DESC = 'Save the current calibration'
PREPROCESSING_CAMERA_CALIBRATION_LOAD_JSON_DIALOG = 'Load a calibration file'
PREPROCESSING_CAMERA_CALIBRATION_DEFAULT_FACTOR = 0.0001
PREPROCESSING_CAMERA_CALIBRATION_N_DECIMALS = 4


# -> For saving/loading jsons
PREPROCESSING_SAVE_CUT = 'Save the current cut profile onto a file'
PREPROCESSING_LOAD_CUT = 'Load cut profile from file'

# -> For auto cut the frame
PREPROCESSING_AUTO_CUT_THRESHOLD_PERCENTAGE = 1
PREPROCESSING_AUTO_CUT_PADDING = 10 # 10 px

# -> For thresholding 
PREPROCESSING_THRESHOLD_DESC = 'Adjust the threshold controls to define the core and contour regions. The selected values will be used for the Smoke Point estimation. You can watch the effect of the selected threshols on the previes on the left. You can also save/load this presets for future use.'
PREPROCESSING_THRESHOLD_FRAME_TITLE = '{} preview'
PREPROCESSING_THESHOLD_CONTROLS_TITLE = '{} controls'
PREPROCESSING_THRESHOLD_PERCENTAGE = '{} threshold value: '
PREPROCESSING_THRESHOLD_INFORMATION = 'ROI Statistics'
PREPROCESSSING_ERROR_THRESHOLD_IMAGE = 'The selected threshold results in a null area, please use a lower one.'
PREPROCESSING_START_ERROR = 'Contour threshold cannot be higher than core threshold!'
PREPROCESSING_THRESHOLD_SUFFIX = ' %'
PREPROCESSING_HEIGHT_INFORMATION_PARSER = '{} px'
PREPROCESSING_AREA_INFORMATION_PARSER = '{} px\u00b2'
PREPROCESSING_INFORMATION_TABLE_WIDTH = 200
PREPROCESSING_INFORMATION_TABLE_COLUMN_HEIGHT = 25
PREPROCESSING_TABLE_PADDING = 2 # 1 px per line division
PREPROCESSING_THRESHOLD_SPIN_WIDTH = 75
PREPROCESSING_THRESHOLD_SAVE = 'Save the current threshold values onto a file'
PREPROCESSING_THRESHOLD_LOAD = 'Load threshold values from file'

# -> Derivative threshold
PREPROCESSING_CONSTANTS_DECIMALS = 5
PREPROCESSING_CONSTANTS_STEP = 0.00001
PREPROCESSING_CONSTANTS_TITLE = 'General Settings'
PREPROCESSING_CONSTANTS_DESC = 'Change general settings and constants used during the analysis'
PREPROCESSING_CONSTANTS_DER_THRESHOLD = 'Derivative threshold:'

# -> For display information
PREPROCESSING_DISPLAY_TITLE = 'Run summary'
PREPROCESSING_DISPLAY_DESC = 'This are the settings that will be applied to the Smoke Point run. You can change them going back to the corresponding tabs. You can also save this general settings for future use.'
PREPROCESSING_DISPLAY_CUT = 'Cut - {} coordinate'
PREPROCESSING_DISPLAY_CUT_WIDTH = 'Cut width'
PREPROCESSING_DISPLAY_THRESHOLD = '{} threshold value'
PREPROCESSING_DISPLAY_WIDTH_VALUE = '{} px'
PREPROCESSING_DISPLAY_THRESHOLD_VALUE = '{} %'
PREPROCESSING_DISPLAY_FACTOR = 'Px to mm conversion factor'
PREPROCESSING_DISPLAY_FACTOR_VALUE = '{} mm/px'
PREPROCESSING_DISPLAY_DERIVATIVE_THRESHOLD = 'Derivative threshold'
PREPROCESSING_DISPLAY_DERIVATIVE_THRESHOLD_VALUE = '{:.5f}'
PREPROCESSING_DISPLAY_INFO_WIDTH = 300
PREPROCESSING_DISPLAY_INFO_HEIGHT = 125

# -> Color for lines
PREPROESSING_CENTER_LINE_COLOR = (255,153,51) # '#ff9933'
PREPROCESSING_WIDTH_LINE_COLOR = (51, 153, 255) # '#3399ff'
PREPROCESSING_LINES_WIDTH = 2

# VideoButtons
VIDEO_BUTTONS_WIDGET_WIDTH = 150
VIDEO_BUTTONS_WIDGET_HEIGHT = 200

# PLOT TABS
TABS_WIDGET_WIDTH = 740
TABS_WIDGET_HEIGHT = 500


# PlotWidget
PLOT_WIDGET_DPI = 100
PLOT_WIDGET_WIDTH = 740
PLOT_WIDGET_HEIGHT = 460
PLOT_WIDGET_TRACE_CONTOUR = '#197278'  
PLOT_WIDGET_TRACE_CORE = '#6CBEED' 
PLOT_WIDGET_TRACE_TIP = '#F46036'

# Centroids Plot
class CentroidTypes(Enum):
    REFERENCE = 0
    VALID = 1
    INVALID = -1

PLOT_CENTROID_REFERENCE_COLOR = '#FFA630'
PLOT_CENTROID_REFERENCE_LINE = '-'
PLOT_CENTROID_SAFE_AREA_LIMITS_COLOR = '#034C3C'
PLOT_CENTROID_SAFE_AREA_LIMITS_LINE = '-.'
PLOT_CENTROID_SAFE_AREA_COLOR = '#3DDC97'
PLOT_CENTROID_SAFE_AREA_ALPHA=0.3
PLOT_CENTROID_VALID_COLOR = '#07004D'
PLOT_CENTROID_VALID_MARKER = 'o'
PLOT_CENTROID_INVALID_COLOR = '#EF2D56'
PLOT_CENTROID_INVALID_MARKER= 'x'

# Height frame plot
PLOT_HEIGHT_TAB_TITLE = 'Height Analysis'
PLOT_HEIGHT_X_AXIS = 'Frames [-]'
PLOT_HEIGHT_Y_AXIS = 'Height [px]'
PLOT_HEIGHT_LABELS = [
    'Flame Height', 
    'Core Height',
    'Tip Height'
]

# Heights polyfitted plot
PLOT_HEIGHT_POLY_TITLE_TAB = 'Tip vs Contour'
PLOT_HEIGHT_POLY_DOTS_COLOR = '#4D9DE0'
PLOT_HEIGHT_POLY_LINE_COLOR ='#FF6666'
PLOT_HEIGHT_POLY_DOTS_LABEL = 'Tip height (H) vs Contour height(h)'
PLOT_HEIGHT_POLY_LINE_LABEL = '10th poly fit'
PLOT_HEIGHTS_POLY_XLABEL = 'Contour height (h) px'
PLOT_HEIGHTS_POLY_YLABEL = 'Tip height (H) px'


# Linear region plot
PLOT_LINEAR_TITLE_TAB = 'Linear Analysis'
PLOT_LINEAR_XLABEL = 'Contour height (h) px'
PLOT_LINEAR_YLABEL = ''
PLOT_LINEAR_DER_LABEL = 'Derivative'
PLOT_LINEAR_REGION_LABEL = 'Linear region'

# SP Plot
PLOT_SP_TITLE_TAB = 'SP Analysis'
PLOT_SP_XLABEL = 'Contour height (h) px'
PLOT_SP_YLABEL = 'Tip height (H) px'
PLOT_SP_POLY_COLOR = PLOT_HEIGHT_POLY_LINE_COLOR
PLOT_SP_LINEAR_POLY_COLOR = '#00A676'
PLOT_SP_POLY_LABEL = PLOT_HEIGHT_POLY_LINE_LABEL
PLOT_SP_LINEAR_POLY_LABEL = 'Linear region fit'
PLOT_SP_POINT_COLOR = '#4E4187'
PLOT_SP_POINT_LABEL = 'Smoke Point {:.2f} px'

# Centroid live plot
PLOT_CENTROID_TAB_TITLE = 'Centroid Analysis'
PLOT_CENTROID_XLABEL = 'Frames [-]'
PLOT_CENTROID_YLABEL = 'X coordinate [px]'


# Information bar

class InformationStatus(Enum):
    IDLE = 'IDLE'
    FRAMES = 'Frame Analysis'
    FRAMES_DONE = 'Frames Done'
    POLYNOMIAL = 'SP Analysis'
    DONE = 'Done'

INFORMATION_BAR_OPERATION_LABEL = 'Operation :'
INFORMATION_BAR_ELAPSED_LABEL = 'Elapsed Time :'
INFORMATION_BAR_ELAPSED_FIELD = '{0:02d}:{1:02d}:{2:02d}'

INFORMATION_LABELS_WIDTH = VIDEO_PLAYER_WIDTH_DEFAULT//2 - 2 # 10 for padding

# Information Tabs display

INFORMATION_TAB_DISPLAY_WIDTH = PLOT_WIDGET_WIDTH - 100 
INFORMATION_TAB_DISPLAY_HEIGHT = 130

# -> Information tab processed frames
INFORMATION_PROCESSED_FRAMES_PLACEHOLDER = '-'
INFORMATION_PROCESSED_CENTROID_DECIMALS = 2
INFORMATION_PROCESSED_CENTROID_LABEL = '{} px'
INFORMATION_PROCESSED_CORE_LABEL = 'Core threshold value:'
INFORMATION_PROCESSED_CONTOUR_LABEL = 'Contour threshold value:'
INFORMATION_PROCESSED_THRESHOLD_FIELD = '{} %'
INFORMATION_PROCESSED_ROW_NUMBER_FRAMES = 'N° of processed frames:'
INFORMATION_PROCESSED_ROW_INVALID_FRAMES = 'N° of invalid frames:'
INFORMATION_PROCESSED_ROW_H_POINTS = 'N° of contour height points (h):'
INFORMATION_PROCESSED_ROW_TIME = 'Processing time:'
INFORMATION_PROCESSED_ROW_CENTROID = 'Centroid reference x:'
INFORMATION_PROCESSED_ROW_TIP_POINTS = 'N° of tip height points (H):'
INFORMATION_PROCESSED_TAB_TITLE = 'Frame process summary'


# -> Information tab polynomial analysis
INFORMATION_POLYNOMIAL_TAB_TITLE = 'Polynomial analysis summary'
INFORMATION_POLYNOMIAL_PLACEHOLDER = '-'
INFORMATION_POLYNOMIAL_THRESHOLD_VALUE = 'Derivative threshold used:'
INFORMATION_POLYNOMIAL_N_POINT_LINEAR_REGION = 'N° of points found in the linear region:'
INFORMATION_POLYNOMIAL_SP_VALUE_FOUND = 'SP found at:'
INFORMATION_POLYNOMIAL_SP_VALUE_FIELD = '{:.2f} px'
INFORMATION_POLYNOMIAL_PROCESSING_TIME = 'Processing time:'