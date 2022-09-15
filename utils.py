import cv2
from matplotlib import pyplot as plt
import math
import numpy as np
import os

# Colors for height boxes
box_colors = {
    'r':(0,0,255),
    'g':(0,255,0),
    'b':(255,0,0),
    'y':(0,255,255),
    'p':(255,0,255)
}


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
    cv2.rectangle(frame, (cc['x'],cc['y']), (cc['x']+cc['w'], cc['y']+cc['h']), box_colors[color],3)


def resultPlotting(sp_results):
    fig = plt.figure()
    # Unpack data
    h = sp_results['height']
    H = sp_results['tip_height']
    tenth_poly = sp_results['tenth_poly']
    der_poly = sp_results['tenth_der']
    linear_poly = sp_results['linear_poly']
    linear_region_start = sp_results['linear_region_start']
    linear_region_end = sp_results['linear_region_end']
    sp_height = sp_results['sp_height']
    sp_Height = sp_results['sp_Height']

    # Analysis of raw data
    plt.subplot(3,1,1)
    # -> Raw height data
    plt.scatter(h,H, color='b', label='Tip Height')
    # -> Poly fitted
    low_bound = math.floor(min(h))
    upp_bound = math.ceil(max(h))
    samples = len(h)
    show_heights = np.linspace(low_bound, upp_bound, samples)
    show_poly_val = np.polyval(tenth_poly, show_heights)
    plt.plot(show_heights, show_poly_val,'r',label='Tenth order poly fitted')
    plt.xlabel('Flame height px')
    plt.ylabel('Flame tip height px')
    plt.grid()
    plt.title('Raw Data Analysis')
    plt.legend()

    # Derivative analysis
    plt.subplot(3,1,2)
    h_sorted = h
    h_sorted.sort()
    show_der_val = np.polyval(der_poly, h_sorted)
    # -> plot raw der values
    plt.scatter(h,show_der_val, color='b', label='Derivative raw data')
    # -> plot der poly
    plt.plot(h_sorted, show_der_val, color='b', label='Derivative of 10th poly')
    # -> Linear region mark
    plt.axvspan(h[linear_region_start], h[linear_region_end], color='r', alpha=0.3, label='Linear Region')
    plt.title('Derivative Analysis')
    plt.xlabel('Flame height px')
    plt.ylabel('2nd derivative of tip height')
    plt.grid()
    plt.legend()

    # SP plot
    plt.subplot(3,1,3)
    plt.plot(show_heights, show_poly_val, color='r', label='10th order poly')
    # -> Linear region reference
    show_linear_poly = np.polyval(linear_poly, h)
    plt.plot(h_sorted, show_linear_poly, color='c', label='Linear Fit')
    # -> Plot SP
    plt.scatter(sp_height, sp_Height, s=50, color='m', label='Smoke Point')
    plt.axhline(y=sp_Height, color='k', linestyle='dashed')
    plt.axvline(x=sp_height, color='k', linestyle='dashed')
    plt.text(0.2,0.8, 'SP HEIGHT {} px'.format(sp_height), transform=plt.gca().transAxes)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

def dataLoader(arg_string):
    # Check if arg is file
    if(os.path.isfile(arg_string)):
        return arg_string

    # Check if is folder with images
    elif(os.path.isdir(arg_string)):
        files = os.listdir(arg_string)
        n_file = len(files)
        file_ = files[0]
        prefix = file_.replace('0000', '%04d')
        return os.path.join(arg_string, prefix)
    
    # Not a valid input exit
    print('Not a valid input!')
    exit(1)