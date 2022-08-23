import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib
from utils import getConnectedComponents
import math
matplotlib.use('tkAgg')

# cv2.namedWindow('Test', cv2.WINDOW_NORMAL)

def borderEnhance(frame):
    sharp_k = np.array([[ 0, -1, 0],
                        [-1, 5, -1],
                        [ 0, -1, 0]])

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # AVG

    n = 3
    p = n -1
    factor = 1/n
    avg = np.zeros_like(gray_frame)
    avg = cv2.addWeighted(gray_frame, factor, avg, factor,0)

    for i in range(p):
        # previous frames
        if i < p/2:
            frame_index = index-math.floor(n/2)+i
        else:
            frame_index = index+math.ceil(n/2)-i

        frame_path = path.format(frame_index)
        temp_frame = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
        avg = cv2.addWeighted(avg, 1.0, temp_frame, factor,0)
    
    avg = gray_frame

    # Contrast enhance
    # contrast = np.zeros_like(gray_frame)
    # c_factor = 1.5
    # b_factor = 0.0
    # for y in range (gray_frame.shape[0]):
    #     for x in range(gray_frame.shape[1]):
    #         contrast[y,x] = np.clip(c_factor*avg[y,x]+b_factor, 0, 255)
    contrast = avg

    sobel_x = cv2.Sobel(contrast, cv2.CV_64F, 0, 1, ksize=3)
    sobel_y = cv2.Sobel(contrast, cv2.CV_64F, 1,0, ksize=5)
    
    abs_grad_x = cv2.convertScaleAbs(sobel_x)
    abs_grad_y = cv2.convertScaleAbs(sobel_y)

    grad = cv2.addWeighted(abs_grad_x, 0.0, abs_grad_y, 1.0,0)

    sharped = cv2.filter2D(grad, ddepth=-1, kernel=sharp_k)

    ret, thresh = cv2.threshold(sharped, 100, 255, cv2.THRESH_BINARY)
    
    morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))

    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, morph_kernel)

    cc = getConnectedComponents(opening, 2)
    cc_mask = cc['cmask'] 
    cc_mask = cv2.morphologyEx(cc_mask, cv2.MORPH_ERODE, morph_kernel)
       
    fig, axs = plt.subplots(1,4)
    fig.suptitle('Gas flame')

    axs[0].imshow(gray_frame, cmap='gray')
    axs[0].set_title('Gray input image')

    axs[1].imshow(cc_mask, cmap='gray')
    axs[1].set_title('Pre-Processed image')
    # Get points for image

    # -> Invert image for data analysis
    inv_opening = cv2.rotate(cc_mask, cv2.ROTATE_180)
    data = []
    for i, row in enumerate(inv_opening):
        for j, col in enumerate(row):
            if(col == 255):
                data.append((j,i))

    data = np.array(data)

    # Get only border
    border = dict()
    for point in data:
        x,y = point
        if x not in border.keys():
            border[x] = y
        else:
            if y > border[x]:
                border[x] = y
    
    border = dict(sorted(border.items()))

    x_data = list(border.keys())
    y_data = list(border.values())

    inv_gray = cv2.rotate(gray_frame, cv2.ROTATE_180)
    axs[2].imshow(inv_gray, cmap='gray')
    axs[2].scatter(x_data, y_data, c='b')
    axs[2].set_title('Points from frame')

    x_ticks = np.arange(0,inv_opening.shape[1], step = 100)    
    axs[2].set_xticks(x_ticks)
    axs[2].invert_yaxis()

    poly = np.polyfit(x_data, y_data, 100)
    poly_val = np.polyval(poly, x_data)

    axs[2].plot(x_data, poly_val, c='r')


    # Get polyderivative
    der_poly = np.polyder(poly, 1)
    der_val = np.polyval(der_poly, x_data)


    cc = getConnectedComponents(opening, 2)
    probando = cc['cmask'] + cc['t_mask']
    prob_op = cv2.morphologyEx(probando, cv2.MORPH_ERODE, morph_kernel)
    axs[3].imshow(probando, cmap='gray')
    # axs[3].plot(x_data, der_val)
    # axs[3].invert_yaxis()

    plt.show()


image = True
#path = '/mnt/shared/SP_18_08_22/sp_test_30fps_1/Basler_acA2040-55uc__23734412__20220818_183353703_%04d.tiff'
path = '/mnt/shared/SP_18_08_22/sp_test_30fps_1/Basler_acA2040-55uc__23734412__20220818_183353703_{:04d}.tiff'
index = 11000
path = path.format(index)
print(path) 
if (image):
    media = cv2.imread(path)

    borderEnhance(media)





