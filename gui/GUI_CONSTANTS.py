from enum import Enum

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
PREPROCESSING_MINIMUM_WIDTH = 100#
PREPROCESSING_SCROLL_WIDTH_STEP = 10
PREPROCESSING_WINDOW_TITLE = 'Preprocessing'
PREPROCESSING_TITLE_MESSAGE= 'Select the region of interest to cut the frames and save processing time'
PREPROCESSING_DESC_MESSAGE = 'Left click on the approximate of the center of the flame and adjust the width of the region, scrolling the wheel. You can use the controls to fine tune the area. You can also save/load this presets for future use.'

# -> For saving/loading jsons
PREPROCESSING_SAVE_CUT = 'Save the current cut profile onto a file'
PREPROCESSING_LOAD_CUT = 'Load cut profile from file'

# -> Color for lines
PREPROESSING_CENTER_LINE_COLOR = (255,153,51) # '#ff9933'
PREPROCESSING_WIDTH_LINE_COLOR = (51, 153, 255) # '#3399ff'
PREPROCESSING_LINES_WIDTH = 2