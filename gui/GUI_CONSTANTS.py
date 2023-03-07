from enum import Enum

# Colors
GUI_RED_ERROR_BG = '#f86e6c'

# LoadWdiget

# -> Display message for QLineEdit used for file selection
LOAD_WIDGET_FILE_DEFAULT_MESSAGE = 'Select a frame folder to process'
LOAD_WIDGET_FILE_DIALOG_HEADER_TITLE = 'Select a folder to process'
LOAD_WIDGET_LOAD_JSON = 'Load settings from file'


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

# -> For saving/loading jsons
PREPROCESSING_SAVE_CUT = 'Save the current cut profile onto a file'
PREPROCESSING_LOAD_CUT = 'Load cut profile from file'

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

# -> For display information
PREPROCESSING_DISPLAY_TITLE = 'Run summary'
PREPROCESSING_DISPLAY_DESC = 'This are the settings that will be applied to the Smoke Point run. You can change them going back to the corresponding tabs. You can also save this general settings for future use.'
PREPROCESSING_DISPLAY_CUT = 'Cut - {} coordinate'
PREPROCESSING_DISPLAY_CUT_WIDTH = 'Cut width'
PREPROCESSING_DISPLAY_THRESHOLD = '{} threshold value'
PREPROCESSING_DISPLAY_WIDTH_VALUE = '{} px'
PREPROCESSING_DISPLAY_THRESHOLD_VALUE = '{} %'
PREPROCESSING_DISPLAY_INFO_WIDTH = 300
PREPROCESSING_DISPLAY_INFO_HEIGHT = 125

# -> Color for lines
PREPROESSING_CENTER_LINE_COLOR = (255,153,51) # '#ff9933'
PREPROCESSING_WIDTH_LINE_COLOR = (51, 153, 255) # '#3399ff'
PREPROCESSING_LINES_WIDTH = 2

# VideoButtons
VIDEO_BUTTONS_WIDGET_WIDTH = 150
VIDEO_BUTTONS_WIDGET_HEIGHT = 200

# PlotWidget
PLOT_WIDGET_WIDTH = 640
PLOT_WIDGET_HEIGHT = 480
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

# Information bar

class InformationStatus(Enum):
    IDLE = 'IDLE'
    FRAMES = 'Frame Analysis'
    FRAMES_DONE = 'Frames Done'

INFORMATION_BAR_OPERATION_LABEL = 'Operation :'
INFORMATION_BAR_ELAPSED_LABEL = 'Elapsed Time :'
INFORMATION_BAR_ELAPSED_FIELD = '{0:02d}:{1:02d}:{2:02d}'

INFORMATION_LABELS_WIDTH = VIDEO_PLAYER_WIDTH_DEFAULT//2 - 2 # 10 for padding

# Information Tabs display

INFORMATION_TAB_DISPLAY_WIDTH = PLOT_WIDGET_WIDTH - 100 
INFORMATION_TAB_DISPLAY_HEIGHT = 125

# -> Information tab processed frames
INFORMATION_PROCESSED_FRAMES_PLACEHOLDER = '-'
INFORMATION_PROCESSED_CENTROID_DECIMALS = 2
INFORMATION_PROCESSED_CENTROID_LABEL = '{} px'
INFORMATION_PROCESSED_ROW_NUMBER_FRAMES = 'N° of processed frames:'
INFORMATION_PROCESSED_ROW_INVALID_FRAMES = 'N° of invalid frames:'
INFORMATION_PROCESSED_ROW_H_POINTS = 'N° of contour height points (h):'
INFORMATION_PROCESSED_ROW_TIME = 'Processing time:'
INFORMATION_PROCESSED_ROW_CENTROID = 'Centroid reference x:'
INFORMATION_PROCESSED_ROW_TIP_POINTS = 'N° of tip height points (H):'