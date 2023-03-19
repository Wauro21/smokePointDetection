import datetime
from core.CONSTANTS import CONTOUR_BOUNDING_BOX_COLOR, CORE_BOUNDING_BOX_COLOR, DERIVATIVE_ORDER, FRAME_CENTROID_COLOR, LINEAR_POLY_ORDER, LINEAR_REGION_ERROR_MESSAGE, MAX_CENTROID_TOLERANCE, MAX_PIXEL_VALUE, NUMBER_OF_CONNECTED_COMPONENTS, POLYNOMIAL_ORDER, REFERENCE_CENTROID_COLOR, SP_FOUND_MESSAGE, SP_THRESHOLD, SUCESSFULL_PROCESSING_MESSAGE, THRESHOLD_VALUES_MESSAGE
import cv2
import numpy as np
from gui.GUI_CONSTANTS import CentroidTypes, FrameTypes
from progress.bar import Bar
import csv
import math
from core.processing_options import argsHandler
import os
from core.utils import checkGenerateFolder, cutHandler, findLinearRegion, getThreshvalues, plotCentroid, verbosePrint, getConnectedComponents, heightBox, resultPlotting, dataLoader
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('tkAgg')


def processHeights(h, H, der_threshold, invalid_frame_counter, show_print=False):
    # -> Fit 10th order poly
    tenth_poly = np.polyfit(h,H, POLYNOMIAL_ORDER)

    # -> Derivative of the 10th order poly
    der_poly = np.polyder(tenth_poly, DERIVATIVE_ORDER)

    # -> Get linear region
    linear_region = findLinearRegion(h, tenth_poly, der_poly, der_threshold)
    # Verify linear region
    if(len(linear_region) <= 2):
        verbosePrint(show_print, LINEAR_REGION_ERROR_MESSAGE.format(len(linear_region),der_threshold))
        linear_poly = None
        sp_height = None
        sp_Height = None
    
    else:
        # Linear region regression
        h_linear = list(linear_region.keys())
        H_linear = list(linear_region.values())
        linear_poly = np.polyfit(h_linear, H_linear, LINEAR_POLY_ORDER)

        # Get the first value over the predicted linear region
        sp_height = None
        sp_Height = None
        h_points = np.linspace(min(h), max(h), len(h))
        h_linear_start = h_linear[0]
        for h_val in h_points:
            # Only search starting from linear region
            if(h_val >= h_linear_start):
                H_val = np.polyval(tenth_poly, h_val)
                H_poly = np.polyval(linear_poly, h_val)
                distance = H_val - H_poly
                if(distance > SP_THRESHOLD):
                    sp_height = h_val
                    sp_Height = H_val
                    break
        if not(sp_height):
            print('SP could not be found with the provided settings.')
        else:
            verbosePrint(show_print, SP_FOUND_MESSAGE.format(sp_height))

    ret_dict = {
    'height':h,					# flame height values
    'tip_height':H,				# Tip height values
    'tenth_poly':tenth_poly,	# 10th poly coef
    'tenth_der':der_poly,		# Derivativa of 10th poly
    'linear_poly':linear_poly,	# Linear region poly
    'linear_region':linear_region, # linea region points
    'sp_height':sp_height,		# flame height at sp
    'sp_Height':sp_Height,		# tip height at sp
    'n_invalid_frames':invalid_frame_counter
    }

    return ret_dict


def frameProcess(frame, cut, core_threshold_value, contour_threshold_value):
    if(cut):
        frame = frame[:, cut['left']: cut['right']]
    
    # -> Convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # -> Apply core and contour umbrals
    ret, core_thresh = cv2.threshold(gray_frame, core_threshold_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
    ret, contour_thresh = cv2.threshold(gray_frame, contour_threshold_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)

    # -> From connected components, get stats
    core_components = getConnectedComponents(core_thresh, NUMBER_OF_CONNECTED_COMPONENTS)
    contour_components = getConnectedComponents(contour_thresh, NUMBER_OF_CONNECTED_COMPONENTS)

    ret_dict = {
        FrameTypes.FRAME: frame, 
        FrameTypes.GRAY: gray_frame,
        FrameTypes.CORE: core_thresh,
        FrameTypes.CONTOUR: contour_thresh, 
        FrameTypes.CORE_CC: core_components,
        FrameTypes.CONTOUR_CC: contour_components
    }

    return ret_dict
    



def smokepoint(args):

    # Check folder for output data
    # -> by default use date for run name unless arg provided
    if(args.SaveValues):
        out_folder_name = '{}_run'.format(args.SaveValues)
        out_path = checkGenerateFolder(out_folder_name)

    # Check if cutting is requested
    cut_info = cutHandler(args.cut)

    # Load frames
    parsed_frames = dataLoader(args.Input)
    media = cv2.VideoCapture(parsed_frames, 0)

    # Unpack info from media
    n_frames = int(media.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(media.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(media.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Set threshold for core and countour
    core_threshold_value = getThreshvalues(args.ThresholdCore)
    contour_threshold_value = getThreshvalues(args.ThresholdContour)
    verbosePrint(args.Verbose, THRESHOLD_VALUES_MESSAGE.format(core_threshold_value,contour_threshold_value))

    # Set the progress bar for verbose
    bar = Bar('Processing', max=n_frames)

    # Storage variables for contour height (h) and tip height (H)
    h = []
    H = []

    # For first frame, get reference centroids
    
    first_frame_flag = True
    # -> The values are set to something impossible
    reference_centroid_x = -float('inf')
    reference_centroid_y = -float('inf')
    

    # Centroid information
    frame_centroids = {
        CentroidTypes.REFERENCE: None,
        CentroidTypes.VALID: {},
        CentroidTypes.INVALID: {},
    }

    # Frame statistics 
    frame_counter = 0
    invalid_frame_counter = 0

    # Frame per frame processing 

    while media.isOpened():
        ret, frame = media.read()
        if not ret: 
            verbosePrint(args.Verbose, SUCESSFULL_PROCESSING_MESSAGE)
            break

        # Update statistics 
        frame_counter += 1
        if(bar): bar.next()

        frame_results = frameProcess(frame, cut_info, core_threshold_value, contour_threshold_value)
    
        # Get contour and tip height
        contour_height = frame_results[FrameTypes.CONTOUR_CC]['h']
        # -> Consider that (0,0) is top left corner
        tip_height = frame_results[FrameTypes.CORE_CC]['y'] - frame_results[FrameTypes.CONTOUR_CC]['y']

        if(first_frame_flag):
            reference_centroid_x = frame_results[FrameTypes.CONTOUR_CC]['cX']
            reference_centroid_y = frame_results[FrameTypes.CONTOUR_CC]['cY']
            frame_centroids[CentroidTypes.REFERENCE] = reference_centroid_x
            first_frame_flag = False

            # First frame heights are considerated valid
            h.append(contour_height)
            H.append(tip_height)

            continue

        # For the rest of the frames        
        # -> Calculate the centroid difference to check if is a valid frame
        invalid_frame_h = []
        invalid_frame_H = []
        frame_centroid = frame_results[FrameTypes.CONTOUR_CC]['cX']
        centroid_diff = abs(frame_centroid - reference_centroid_x)

        if(centroid_diff > args.CentroidTolerance):
            frame_centroids[CentroidTypes.INVALID][frame_counter] = frame_centroid
            invalid_frame_counter += 1
            invalid_frame_h.append(contour_height)
            invalid_frame_H.append(tip_height)
            continue
        
        # If the data is valid, append it
        frame_centroids[CentroidTypes.VALID][frame_counter] = frame_centroid
        h.append(contour_height)
        H.append(tip_height)

        # End of media reading
    
    bar.finish()
    media.release()

    # Polynomial Analysis
    polynomial_results = processHeights(h, H, args.DerivativeThreshold, invalid_frame_counter, args.Verbose)

    # Add the invalid frames values
    polynomial_results['invalid_frames_h'] = invalid_frame_h
    polynomial_results['invalid_frames_H'] = invalid_frame_H

    # Add centroid information
    polynomial_results['centroids'] = frame_centroids

    if(args.SaveValues):
        np.savetxt(os.path.join(out_path,'flame_height.csv'), polynomial_results['height'],delimiter=',')
        np.savetxt(os.path.join(out_path,'tip_height.csv'), polynomial_results['tip_height'],delimiter=',')

    return polynomial_results
        



if __name__ == '__main__':
    args = argsHandler()
    sp_vals = smokepoint(args)
    print('Invalid Frames : {}'.format(sp_vals['n_invalid_frames']))
    resultPlotting(sp_vals,True)