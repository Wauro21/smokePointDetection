import cv2

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
