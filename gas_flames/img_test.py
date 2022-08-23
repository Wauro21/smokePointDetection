import cv2
import numpy as np

MAX_CONTRAST = 2
MIN_CONTRAST = 0

MAX_BRIGHT = 1
MIN_BRIGHT = 0

def on_contrast(value):
    contrast_value = (MAX_CONTRAST-MIN_CONTRAST)*value/100
    img_copy = img.copy()
    # Add contrast
    cv2.imshow(window, img_copy*contrast_value)

def on_brightness(value):
    brightness_value = (MAX_BRIGHT-MIN_BRIGHT)*value/100
    img_copy = img.copy()
    # Add contrast
    cv2.imshow(window, img_copy+brightness_value)


window = 'image'
cv2.namedWindow(window, cv2.WINDOW_NORMAL)

img = cv2.imread('demo.tiff')

sobel_y = cv2.Sobel(img,cv2.CV_64F, 1, 0, ksize=3)


cv2.imshow(window, img)

cv2.createTrackbar('Contrast', window, 0, 100, on_contrast)
# cv2.createTrackbar('Brigthness', window, 0, 100, on_brightness)

cv2.waitKey(0)
cv2.destroyAllWindows()



