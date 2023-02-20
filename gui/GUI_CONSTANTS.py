from enum import Enum

# LoadWdiget

# -> Display message for QLineEdit used for file selection
LOAD_WIDGET_FILE_DEFAULT_MESSAGE = 'Select a frame folder to process'
LOAD_WIDGET_FILE_DIALOG_HEADER_TITLE = 'Select a folder to process'


# VideoPlayer

VIDEO_PLAYER_BG_COLOR = '#303539'

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