from enum import Enum

# Colors
GUI_RED_ERROR_BG = '#f86e6c'

# LoadWdiget

# -> Display message for QLineEdit used for file selection
LOAD_WIDGET_FILE_DEFAULT_MESSAGE = 'Select a frame folder to process'
LOAD_WIDGET_FILE_DIALOG_HEADER_TITLE = 'Select a folder to process'


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
PREPROCESSING_THRESHOLD_FRAME_TITLE = '{} preview'
PREPROCESSING_THESHOLD_CONTROLS_TITLE = '{} controls'
PREPROCESSING_THRESHOLD_PERCENTAGE = '{} threshold value: '
PREPROCESSING_THRESHOLD_INFORMATION = 'ROI Statistics'
PREPROCESSSING_ERROR_THRESHOLD_IMAGE = 'The selected threshold results in a null area, please use a lower one.'
PREPROCESSING_START_ERROR = 'Contour threshold cannot be higher than core threshold!'
PREPROCESSING_THRESHOLD_SUFFIX = ' %'
PREPROCESSING_HEIGHT_INFORMATION_PARSER = '{} px'
PREPROCESSING_AREA_INFORMATION_PARSER = '{} px\u00b2'

# -> Color for lines
PREPROESSING_CENTER_LINE_COLOR = (255,153,51) # '#ff9933'
PREPROCESSING_WIDTH_LINE_COLOR = (51, 153, 255) # '#3399ff'
PREPROCESSING_LINES_WIDTH = 2

# VideoButtons
VIDEO_BUTTONS_WIDGET_WIDTH = 150
VIDEO_BUTTONS_WIDGET_HEIGHT = 200

# PlotWidget
PLOT_WIDGET_WIDTH = 640
PLOT_WIDGET_HEIGHT = 450
PLOT_WIDGET_TRACE_A_COLOR = '#197278'
PLOT_WIDGET_TRACE_B_COLOR = '#6CBEED'