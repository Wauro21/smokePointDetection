from CONSTANTS import CONTOUR_BOUNDING_BOX_COLOR, CORE_BOUNDING_BOX_COLOR, CUT_ARGS_ERROR_MESSAGE, DERIVATIVE_ORDER, FRAME_CENTROID_COLOR, LINEAR_POLY_ORDER, LINEAR_REGION_ERROR_MESSAGE, MAX_CENTROID_TOLERANCE, MAX_PIXEL_VALUE, NUMBER_OF_CONNECTED_COMPONENTS, POLYNOMIAL_ORDER, REFERENCE_CENTROID_COLOR, SP_FOUND_MESSAGE, SP_THRESHOLD, SUCESSFULL_PROCESSING_MESSAGE, THRESHOLD_VALUES_MESSAGE
import cv2
import numpy as np
from progress.bar import Bar
import csv
import math
from processing_options import argsHandler
import os
from utils import checkGenerateFolder, getThreshvalues, plotCentroid, verbosePrint, getConnectedComponents, heightBox, resultPlotting, dataLoader
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('tkAgg')


def processHeights(h, H, der_threshold, invalid_frame_counter):
    # -> Fit 10th order poly
    tenth_poly = np.polyfit(h,H, POLYNOMIAL_ORDER)

    # -> Derivative of the 10th order poly
    der_poly = np.polyder(tenth_poly, DERIVATIVE_ORDER)

    # -> Get linear region
    linear_region_flag = True
    linear_region_start = -float('inf')
    linear_region_end = float('inf')
    linear_region_points = {}

    for flame_pos, flame_height in enumerate(h):
        poly_eval = abs(np.polyval(der_poly, flame_height))
        if(poly_eval <= der_threshold):
            linear_region_points[flame_height] = np.polyval(tenth_poly, flame_height)
            if(linear_region_flag):
                linear_region_start = flame_pos
                linear_region_flag = False
                continue
            
            linear_region_end = flame_pos

    # Check if the linear region was found
    if(len(linear_region_points) <= 2):
        print(LINEAR_REGION_ERROR_MESSAGE.format(len(linear_region_points),args.DerivativeThreshold))
        linear_poly = None
        sp_height = None
        sp_Height = None
    
    else:
        # Linear region regression
        linear_poly = np.polyfit(list(linear_region_points.keys()),list( linear_region_points.values()), LINEAR_POLY_ORDER)

        # Get the first value over the predicted linear region
        sp_height = -float('inf')
        sp_Height = -float('inf')

        for flame_pos in range(linear_region_start, len(h)):
            flame_height = h[flame_pos]
            poly_H_val = np.polyval(tenth_poly, flame_height)
            poly_linear_val = np.polyval(linear_poly, flame_height)
            distance = poly_H_val - poly_linear_val

            if(distance > SP_THRESHOLD): 
                sp_height = flame_height
                sp_Height = poly_H_val
                break
        verbosePrint(args.Verbose, SP_FOUND_MESSAGE.format(sp_height, flame_pos))

    ret_dict = {
    'height':h,					# flame height values
    'tip_height':H,				# Tip height values
    'tenth_poly':tenth_poly,	# 10th poly coef
    'tenth_der':der_poly,		# Derivativa of 10th poly
    'linear_poly':linear_poly,	# Linear region poly
    'linear_region_start':linear_region_start,
    'linear_region_end':linear_region_end,
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
        'frame': frame, 
        'gray': gray_frame,
        'core': core_thresh,
        'contour': contour_thresh, 
        'core_cc': core_components,
        'contour_cc': contour_components
    }

    return ret_dict
    



def smokepoint(args):

    # Check folder for output data
    out_path = checkGenerateFolder(args.runName)

    out_frame_folder = checkGenerateFolder(os.path.join(out_path, 'frames'))

    # Load frames
    parsed_frames = dataLoader(args.Input)
    media = cv2.VideoCapture(parsed_frames, 0)

    # Unpack info from media
    n_frames = int(media.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(media.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(media.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Set threshold for core and countour
    core_threshold_value = getThreshvalues(args.TresholdCore)
    contour_threshold_value = getThreshvalues(args.TresholdContour)
    verbosePrint(args.Verbose, THRESHOLD_VALUES_MESSAGE.format(core_threshold_value,contour_threshold_value))

    # Set the progress bar for verbose
    bar = None 
    if args.Verbose:
        bar = Bar('Processing', max=n_frames)
    
    # Generate Window for displaying progress
    if(args.Display):
        cv2.namedWindow('input', cv2.WINDOW_NORMAL)

    # Storage variables for contour height (h) and tip height (H)
    h = []
    H = []

    # For first frame, get reference centroids
    
    first_frame_flag = True
    # -> The values are set to something impossible
    reference_centroid_x = -float('inf')
    reference_centroid_y = -float('inf')

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

        # Check if cut is needed

        cut_info = None
        if(args.cut):
            center_line = width//2
            cut = args.cut //2
            
            cut_info = {
                'left': center_line-cut,
                'right': center_line+cut,
                'center_line': center_line
            }

        frame_results = frameProcess(frame, cut_info, core_threshold_value, contour_threshold_value)
    
        # Get contour and tip height
        contour_height = frame_results['contour_cc']['h']
        # -> Consider that (0,0) is top left corner
        tip_height = frame_results['core_cc']['y'] - frame_results['contour_cc']['y']

        if(first_frame_flag):
            reference_centroid_x = frame_results['contour_cc']['cX']
            reference_centroid_y = frame_results['contour_cc']['cY']
            first_frame_flag = False

            # First frame heights are considerated valid
            h.append(contour_height)
            H.append(tip_height)

            continue

        # For the rest of the frames

        # -> Generate height boxes to display
        if(args.Boxes): 
            heightBox(frame, frame_results['core_cc'], CORE_BOUNDING_BOX_COLOR)
            heightBox(frame, frame_results['contour_cc'], CONTOUR_BOUNDING_BOX_COLOR)

        # -> Draw the reference centroids and the actual centroid
        if(args.Centroids):
            plotCentroid(frame, reference_centroid_x, reference_centroid_y, REFERENCE_CENTROID_COLOR)
            plotCentroid(frame, frame_results['contour_cc']['cX'], frame_results['contour_cc']['cY'], FRAME_CENTROID_COLOR)
             
        
        # Calculate the centroid difference to check if is a valid frame
        invalid_frame_h = []
        invalid_frame_H = []
        centroid_diff = abs(frame_results['contour_cc']['cX'] - reference_centroid_x)

        if(centroid_diff > MAX_CENTROID_TOLERANCE):
            invalid_frame_counter += 1
            invalid_frame_h.append(contour_height)
            invalid_frame_H.append(tip_height)
            continue
        
        # If the data is valid, append it
        h.append(contour_height)
        H.append(tip_height)

        if(args.Display):
            cv2.imshow('input', frame)
            if cv2.waitKey(1) == ord('q'):
                break
        # End of media reading
    
    if(bar): bar.finish()
    media.release()


    polynomial_results = processHeights(h, H, args.DerivativeThreshold, invalid_frame_counter)

    # Add the invalid frames values
    polynomial_results['invalid_frames_h'] = invalid_frame_h
    polynomial_results['invalid_frames_H'] = invalid_frame_H

    if(args.saveFig):
        np.savetxt(os.path.join(out_path,'flame_height.csv'), polynomial_results['height'],delimiter=',')
        np.savetxt(os.path.join(out_path,'tip_height.csv'), polynomial_results['tip_height'],delimiter=',')
        np.savetxt(os.path.join(out_path,'n_invalid_frames.csv'), polynomial_results['n_invalid_frames'])


    return polynomial_results
        



if __name__ == '__main__':
    args = argsHandler()
    sp_vals = smokepoint(args)
    print('Invalid Frames : {}'.format(sp_vals['n_invalid_frames']))
    resultPlotting(sp_vals,True)