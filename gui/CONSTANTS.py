# -> Processing Constants

MAX_PIXEL_VALUE = 255
MAX_CENTROID_TOLERANCE = 10 #px, converted from the 1mm by authors
DERIVATIVE_LOW_BOUND = 2e-5
SP_THRESHOLD = 1 #px, converted from the 0,1mm by authors

NUMBER_OF_CONNECTED_COMPONENTS = 4
POLYNOMIAL_ORDER = 10
DERIVATIVE_ORDER = 2
LINEAR_POLY_ORDER = 1

# -> Plotting constants
# Drawing values
CENTROID_RADIUS = 10
REFERENCE_CENTROID_COLOR = (48,166,255)
FRAME_CENTROID_COLOR = (77,0,7)

# Fig save padding
FIG_PADDING = 200 #px

# -> Displayed messages

THRESHOLD_VALUES_MESSAGE = "[INFO] The threshold values are:\n\tCore: {}\n\tContour: {}"
SUCESSFULL_PROCESSING_MESSAGE = "[INFO] End of stream, processing is done"
CUT_ARGS_ERROR_MESSAGE = "[ERROR] Too many arguments for cut option."
LINEAR_REGION_ERROR_MESSAGE = "No enough points ({}) were found to set the linear region with derivative threshold of {}"
SP_FOUND_MESSAGE = 'SP height found {} at frame {}'

# -> Bounding Boxes for regions
CORE_BOUNDING_BOX_COLOR = (120, 114, 25)
CONTOUR_BOUNDING_BOX_COLOR = (237, 190, 108)
