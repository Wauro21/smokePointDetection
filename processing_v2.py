import cv2
import numpy as np
from progress.bar import Bar
import csv
import math
from processing_options import argsHandler
import os
from utils import verbosePrint, getConnectedComponents, heightBox

# Default Values
MAX_PIXEL_VALUE = 255
MAX_CENTROID_TOLERANCE = 10 #px, converted from the 1mm by authors

# Drawing values
CENTROID_RADIUS = 10


def smokepoint(args):
    # Load the data (video or folder)
    media = cv2.VideoCapture(args.Input)
    n_frames = int(media.get(cv2.CAP_PROP_FRAME_COUNT))
    # Set threshold for core and countour
    core_threshold_value = round(MAX_PIXEL_VALUE*args.ThresholdCore/100)
    contour_threshold_value = round(MAX_PIXEL_VALUE*args.ThresholdContour/100)

    verbosePrint(args.Verbose,"[INFO] The threshold values are:\n\tCore: {}\n\tContour: {}".format(core_threshold_value,contour_threshold_value))

    if args.Verbose:
        bar = Bar('Processing', max=n_frames)
    else:
        bar = None

    if(args.Display):
        cv2.namedWindow("input", cv2.WINDOW_NORMAL)

    h = []
    H = []
    first_frame_flag = True
    reference_centroid_x = -float('inf')
    reference_centroid_y = -float('inf')
    invalid_frame_counter = 0
    # Perform frame by frame processing
    while media.isOpened():
        ret, frame = media.read()
        if not ret:
            verbosePrint(args.Verbose, "[INFO] End of stream, processing is done")
            break

        # -> Convert to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # -> Apply core and contour umbrals
        ret, core_thresh = cv2.threshold(gray_frame, core_threshold_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
        ret, contour_thresh = cv2.threshold(gray_frame, contour_threshold_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)

        # -> From connected components, get stats
        core_components = getConnectedComponents(core_thresh,4)
        contour_components = getConnectedComponents(contour_thresh,4)

        # -> Get heights and centroid of the first frame
        contour_height = contour_components['h']
        # Consider that (0,0) is top left corner
        tip_height = core_components['y'] - contour_components['y']

        if(args.Boxes):
            heightBox(frame, core_components,'r')
            heightBox(frame, contour_components,'g')


        if(first_frame_flag):
            reference_centroid_x = contour_components['cX']
            reference_centroid_y = contour_components['cY']
            first_frame_flag = False
            continue

        # Draw reference centroid and frame centroid [TO-DO:ARGUMENT?]
        cv2.circle(frame, (int(reference_centroid_x), int(reference_centroid_y)), CENTROID_RADIUS, (255,0,255),-1)
        cv2.circle(frame, (int(contour_components['cX']),int(contour_components['cY'])), CENTROID_RADIUS, (255,0,0),-1)

        centroid_diff = abs(contour_components['cX']-reference_centroid_x)

        # Check if frame is not valid
        if(centroid_diff > MAX_CENTROID_TOLERANCE):
            invalid_frame_counter +=1
            verbosePrint(args.Verbose, "Invalid Frame {}".format(invalid_frame_counter))
            continue

        # If valid, get height data
        h.append(contour_height)
        H.append(tip_height)

        if(bar):
            bar.next()

        if(args.Display):
            cv2.imshow('input', frame)
            if cv2.waitKey(1) == ord('q'):
                break

     # End of media reading

    if(bar):
        bar.finish()
    media.release()







if __name__ == '__main__':
    args = argsHandler()
    smokepoint(args)
