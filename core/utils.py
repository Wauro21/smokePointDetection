import json
from core.CONSTANTS import CENTROID_RADIUS, MAX_PIXEL_VALUE
import cv2
from matplotlib import pyplot as plt
import math
import numpy as np
import os
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtCore import Qt
from gui.GUI_CONSTANTS import PLOT_CENTROID_INVALID_COLOR, PLOT_CENTROID_INVALID_MARKER, PLOT_CENTROID_REFERENCE_COLOR, PLOT_CENTROID_REFERENCE_LINE, PLOT_CENTROID_SAFE_AREA_ALPHA, PLOT_CENTROID_SAFE_AREA_COLOR, PLOT_CENTROID_SAFE_AREA_LIMITS_COLOR, PLOT_CENTROID_SAFE_AREA_LIMITS_LINE, PLOT_CENTROID_VALID_COLOR, PLOT_CENTROID_VALID_MARKER, PLOT_CENTROID_XLABEL, PLOT_CENTROID_YLABEL, PLOT_HEIGHT_LABELS, PLOT_HEIGHT_POLY_DOTS_COLOR, PLOT_HEIGHT_POLY_DOTS_LABEL, PLOT_HEIGHT_POLY_LINE_COLOR, PLOT_HEIGHT_POLY_LINE_LABEL, PLOT_HEIGHT_X_AXIS, PLOT_HEIGHT_Y_AXIS, PLOT_HEIGHTS_POLY_XLABEL, PLOT_HEIGHTS_POLY_YLABEL, PLOT_LINEAR_DER_LABEL, PLOT_LINEAR_REGION_LABEL, PLOT_LINEAR_XLABEL, PLOT_LINEAR_YLABEL, PLOT_SP_LINEAR_POLY_COLOR, PLOT_SP_LINEAR_POLY_LABEL, PLOT_SP_POINT_COLOR, PLOT_SP_POINT_LABEL, PLOT_SP_POLY_COLOR, PLOT_SP_POLY_LABEL, PLOT_SP_XLABEL, PLOT_SP_YLABEL, PLOT_WIDGET_TRACE_CONTOUR, PLOT_WIDGET_TRACE_CORE, PLOT_WIDGET_TRACE_TIP, VIDEO_PLAYER_BG_COLOR_BGR, VIDEO_PLAYER_BG_COLOR_GRAY, VIDEO_PLAYER_HEIGHT_DEFAULT, VIDEO_PLAYER_WIDTH_DEFAULT, CentroidTypes

# Returns the biggest linear region
def findLinearRegion(h, poly_coef, der_coef, der_threshold):

    h_min = min(h)
    h_max = max(h)
    h_points = np.linspace(h_min, h_max, len(h))

    linear_regions = {}
    region_counter = 0
    found_region = False
    for flame_height in h_points:
        poly_eval = abs(np.polyval(der_coef, flame_height))
        if(poly_eval <= der_threshold):
            
            if not(found_region):
                # is the first linear point
                found_region = True
                # initialize dict 
                linear_regions[region_counter] = {}

            # In any case add it to the corresponding region
            linear_regions[region_counter][flame_height] = np.polyval(poly_coef, flame_height)
            
        elif(found_region):
            # The linear region ends
            found_region = False
            region_counter += 1

    # Select the biggest region
    last_region = -1
    biggest_region = None
    
    for region in linear_regions:
        n_points = len(linear_regions[region])
        if(n_points > last_region):
            last_region = n_points
            biggest_region = linear_regions[region]

    return biggest_region        


# Prints the message only if verbose mode is active
def verbosePrint(control, text):
    if(control):
        print(text)

def getConnectedComponents(threshold_image, connect):
    return_dict = {
        'x':0,
        'y':0,
        'w':0,
        'h':0,
        'area':-1,
        'cX':0,
        'cY':0,
        'cmask':None
    }

    cc = cv2.connectedComponentsWithStats(threshold_image, connect, cv2.CV_32S)

    n_labels, labels, stats, centroids = cc
    # Start at 1 to ignore background
    for i in range(1,n_labels):
        # Save only the biggest area
        area = stats[i, cv2.CC_STAT_AREA]
        if(area > return_dict['area']):
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            (cX,cY) = centroids[i]
            component_mask = (labels==i).astype("uint8")*255
            return_dict = {
                'x':x,
                'y':y,
                'w':w,
                'h':h,
                'area':area,
                'cX':cX,
                'cY':cY,
                'cmask':component_mask
            }
    return return_dict

def px2mm(value):
    # As calculations performed by the authors
    M_PX_CM = 0.1038
    C_PX_CM = 3.55
    return (M_PX_CM*value)+C_PX_CM

def heightBox(frame, cc, color):
    cv2.rectangle(frame, (cc['x'],cc['y']), (cc['x']+cc['w'], cc['y']+cc['h']), color,3)


def plotCentroid(frame, rcX, rcY, color):
    cv2.circle(frame, (int(rcX), int(rcY)), CENTROID_RADIUS, color,-1)

def resultPlotting(sp_results,args):
    # Unpack data
    h = np.array(sp_results['height'])
    H = np.array(sp_results['tip_height'])
    tenth_poly = sp_results['tenth_poly']
    der_poly = sp_results['tenth_der']
    linear_poly = sp_results['linear_poly']
    linear_region = sp_results['linear_region']
    sp_height = sp_results['sp_height']
    sp_Height = sp_results['sp_Height']
    inv_x = sp_results['invalid_frames_h']
    inv_y = sp_results['invalid_frames_H']
    centroid_info = sp_results['centroids']

    # Height analysis
    height_plots = plt.figure()
    ax = height_plots.add_subplot(111)
    
    # -> Tip data
    core_height = h-H
    n_valid_frames = len(h)
    frame_vector = np.linspace(0, n_valid_frames-1, n_valid_frames)

    # -> Plot
    ax.plot(frame_vector, h, label=PLOT_HEIGHT_LABELS[0], color=PLOT_WIDGET_TRACE_CONTOUR)
    ax.plot(frame_vector, core_height, label=PLOT_HEIGHT_LABELS[1], color=PLOT_WIDGET_TRACE_CORE)
    ax.plot(frame_vector, H, label=PLOT_HEIGHT_LABELS[2], color=PLOT_WIDGET_TRACE_TIP)
    ax.grid()
    ax.set_xlabel(PLOT_HEIGHT_X_AXIS)
    ax.set_ylabel(PLOT_HEIGHT_Y_AXIS)
    ax.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=3)

    # Centroid analysis
    centroid_plot = plt.figure()
    ax = centroid_plot.add_subplot(111)

    #-> Centoid Data
    valid_points = centroid_info[CentroidTypes.VALID]
    invalid_points = centroid_info[CentroidTypes.INVALID]
    ref_centroid = centroid_info[CentroidTypes.REFERENCE]

    # -> Plot

    # ---> Reference centroid
    ax.axhline(y=ref_centroid, color=PLOT_CENTROID_REFERENCE_COLOR, linestyle=PLOT_CENTROID_REFERENCE_LINE, label='Reference')

    # ---> Tolerance area
    tolerance = args.CentroidTolerance
    upper = ref_centroid + tolerance
    lower = ref_centroid - tolerance
    ax.axhline(y=upper, color=PLOT_CENTROID_SAFE_AREA_LIMITS_COLOR, linestyle=PLOT_CENTROID_SAFE_AREA_LIMITS_LINE)
    ax.axhline(y=lower, color=PLOT_CENTROID_SAFE_AREA_LIMITS_COLOR, linestyle=PLOT_CENTROID_SAFE_AREA_LIMITS_LINE)
    ax.axhspan(lower, upper, color=PLOT_CENTROID_SAFE_AREA_COLOR, alpha=PLOT_CENTROID_SAFE_AREA_ALPHA, label='Safe area')

    # ---> Scatter valid centroids
    valid_points_frames = list(valid_points.keys())
    valid_points_values = list(valid_points.values())
    ax.scatter(valid_points_frames, valid_points_values, color=PLOT_CENTROID_VALID_COLOR, marker=PLOT_CENTROID_VALID_MARKER, label='Valid')

    # ---> Scatter invalid centroid
    invalid_points_frames = list(invalid_points.keys())
    invalid_points_values = list(invalid_points.values())
    ax.scatter(invalid_points_frames, invalid_points_values, color=PLOT_CENTROID_INVALID_COLOR, marker=PLOT_CENTROID_INVALID_MARKER, label='Invalid')
    
    ax.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=4)
    ax.set_xlabel(PLOT_CENTROID_XLABEL)
    ax.set_ylabel(PLOT_CENTROID_YLABEL)
    ax.grid()
    

    # SP polynomial plot
    polyPlot = plt.figure()
    ax = polyPlot.add_subplot(111)

    # -> Data
    h_min = math.floor(min(h))
    h_max = math.ceil(max(h))
    samples = len(h)
    poly_h = np.linspace(h_min, h_max, samples)
    poly_values = np.polyval(tenth_poly, poly_h)

    # -> Plot
    ax.scatter(h, H, color=PLOT_HEIGHT_POLY_DOTS_COLOR, label=PLOT_HEIGHT_POLY_DOTS_LABEL)
    ax.plot(poly_h, poly_values, color=PLOT_HEIGHT_POLY_LINE_COLOR, label=PLOT_HEIGHT_POLY_LINE_LABEL)

    ax.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=4)
    ax.set_xlabel(PLOT_HEIGHTS_POLY_XLABEL)
    ax.set_ylabel(PLOT_HEIGHTS_POLY_YLABEL)
    ax.grid()
    
    # Linear region analysis
    # -> Check if linear region was found
    if(linear_region):

        linearPlot = plt.figure()
        ax = linearPlot.add_subplot(111)

        # -> Data
        der_values = np.polyval(der_poly, poly_h)
        l_h = list(linear_region.keys())

        # -> Plot
        ax.plot(poly_h, der_values, label=PLOT_LINEAR_DER_LABEL)
        # Plot linear region area
        ax.axvspan(l_h[0], l_h[-1], color='r', alpha=0.3, label=PLOT_LINEAR_REGION_LABEL)
        
        ax.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=4)
        ax.set_xlabel(PLOT_LINEAR_XLABEL)
        ax.set_ylabel(PLOT_LINEAR_YLABEL)
        ax.grid()

    # SP plot
    if(sp_height):
        spPlot = plt.figure()
        ax = spPlot.add_subplot(111)

        # -> Data

        linear_poly_values = np.polyval(linear_poly, poly_h)

        # -> Plot
        ax.plot(poly_h, poly_values, color=PLOT_SP_POLY_COLOR, label=PLOT_SP_POLY_LABEL)
        ax.plot(poly_h, linear_poly_values, color=PLOT_SP_LINEAR_POLY_COLOR, label=PLOT_SP_LINEAR_POLY_LABEL)
        # Plot sp
        ax.axhline(y=sp_Height, color='k', linestyle='dashed')
        ax.axvline(x=sp_height, color='k', linestyle='dashed')
        ax.scatter(sp_height, sp_Height, s=50, color=PLOT_SP_POINT_COLOR, label=PLOT_SP_POINT_LABEL.format(sp_height))
        
        ax.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=4)
        ax.set_xlabel(PLOT_SP_XLABEL)
        ax.set_ylabel(PLOT_SP_YLABEL)
        ax.grid()
    
    if(args.Display):
        plt.show()

    if(args.SaveValues):
        out_path = '{}_run'.format(args.SaveValues)
        if not(os.path.isdir(out_path)):
            print('Save path does not exists!')
            exit(1)
        
        height_plots.savefig(os.path.join(out_path, 'height_analysis.pdf'))
        polyPlot.savefig(os.path.join(out_path, 'polynomial_analysis.pdf'))
        if(linear_region): linearPlot.savefig(os.path.join(out_path, 'linear_region_analysis.pdf'))
        if(sp_height): spPlot.savefig(os.path.join(out_path, 'sp_analysis.pdf'))


def dataLoader(arg_string):
    # Check if arg is file
    if(os.path.isfile(arg_string)):
        return arg_string

    # Check if is folder with images
    elif(os.path.isdir(arg_string)):
        files = os.listdir(arg_string)
        files.sort()
        file_ = files[0]
        prefix = file_.replace('0000', '%04d')
        return os.path.join(arg_string, prefix)
    
    # Not a valid input exit
    print('Not a valid input!')
    exit(1)

def checkGenerateFolder(path):
    if not(os.path.isdir(path)):
        os.mkdir(path)    
    return path

def getThreshvalues(percentage):
    return round(MAX_PIXEL_VALUE*percentage/100)

def convert2QT(cv_img, resize=True):
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch*w
        converted = QImage(rgb_img, w, h, bytes_per_line, QImage.Format_RGB888)
        if(resize):
            converted = converted.scaled(680, 480,Qt.KeepAspectRatio)
        return QPixmap.fromImage(converted)


def resizeFrame(frame, target=[VIDEO_PLAYER_HEIGHT_DEFAULT, VIDEO_PLAYER_WIDTH_DEFAULT]):
        # Unpack frame info
        try: 
            h, w, c = frame.shape
        except:
            h, w = frame.shape
            c = None
        # Calculate aspect ratio
        ar = w/h
        # Target dimensions
        H, W = target      
        #Calculate the possible dimensions
        # -> Fix height
        nH = H
        # -> From aspect ratio get new width
        nW = round(ar*nH)
        # -> Apply resizing to the possible dimensions that keep the aspect ratio
        resized_frame = cv2.resize(frame, (nW, nH))

        # Generate the final target size frame add color to bg
        if(c):
            f_frame = np.ones((H, W, c), np.uint8)
            for i in range(c):
                f_frame[:,:,i] =  f_frame[:,:,i] *VIDEO_PLAYER_BG_COLOR_BGR[i]
        else:
            f_frame = np.ones((H, W), np.uint8)
            f_frame[:,:] =  f_frame[:,:] *VIDEO_PLAYER_BG_COLOR_GRAY

        # Position resized frame inside final frame
        # -> Calculate the left-most edge of the resized frame inside de final frame
        aH, aW = (H-nH)//2, (W - nW)//2
        # -> Position the frame 
        f_frame[aH:aH+nH, aW:aW+nW] = resized_frame

        return f_frame

def cutHandler(cut_arg):
    ret_dict = {
        'left':None,
        'right': None,
    }

    # Check if the arg is passed at all
    if not (cut_arg):
        return None
    
    # Check if values are passed
    n_args = len(cut_arg)
    if(n_args == 2):
        try:
            ret_dict['left'] = cut_arg[0]
            ret_dict['right'] = cut_arg[1]
            return ret_dict
        
        except:
            print('Invalid cut information. Should be two integers values separated by a space, i.e. 100 200. But received {}'.format(cut_arg))
            exit(1)
    
    # Check if json cut file provided
    arg_file = cut_arg[0]
    if(os.path.isfile(arg_file)):
        with open(arg_file, 'r') as json_file:
            try:
                json_dict = json.load(json_file)

                ret_dict['left'] = json_dict['left']
                ret_dict['right'] = json_dict['right']

                return ret_dict
            
            except:
                print('Invalid cut json file format!')
                exit(1)

    else:
        print('Could not find cut json file : {}'.format(cut_arg))



