# Import required modules
import cv2
import numpy as np
import os
import glob
 
cv2.namedWindow('img', cv2.WINDOW_NORMAL)
 
# Define the dimensions of checkerboard
CHECKERBOARD = (4, 4)
 
 
# stop the iteration when specified
# accuracy, epsilon, is reached or
# specified number of iterations are completed.
criteria = (cv2.TERM_CRITERIA_EPS +
            cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
 
# Vector for 3D points
threedpoints = []
 
# Vector for 2D points
twodpoints = []
 
 
#  3D points real world coordinates
objectp3d = np.zeros((1, CHECKERBOARD[0]
                      * CHECKERBOARD[1],
                      3), np.float32)
objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0],
                               0:CHECKERBOARD[1]].T.reshape(-1, 2)
prev_img_shape = None
 
 
# Extracting path of individual image stored
# in a given directory. Since no path is
# specified, it will take current directory
# jpg files alone
images = glob.glob('/home/mauricio/basler_calibration/*.tiff')
 
for filename in images:
    image = cv2.imread(filename)
    grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
    # Find the chess board corners
    # If desired number of corners are
    # found in the image then ret = true
    ret, corners = cv2.findChessboardCornersSB(
                    grayColor, CHECKERBOARD,
                    cv2.CALIB_CB_ADAPTIVE_THRESH
                    + cv2.CALIB_CB_FAST_CHECK +
                    cv2.CALIB_CB_NORMALIZE_IMAGE)
    print(ret)
 
    # If desired number of corners can be detected then,
    # refine the pixel coordinates and display
    # them on the images of checker board
    if ret == True:
        threedpoints.append(objectp3d)
 
        # Refining pixel coordinates
        # for given 2d points.
        corners2 = cv2.cornerSubPix(
            grayColor, corners, (11, 11), (-1, -1), criteria)
 
        twodpoints.append(corners2)
 
        # Draw and display the corners
        image = cv2.drawChessboardCorners(image,
                                          CHECKERBOARD,
                                          corners2, ret)
 
    #cv2.imshow('img', image)
    #cv2.waitKey(0)
 
#cv2.destroyAllWindows()
 
h, w = image.shape[:2]
 
 
# Perform camera calibration by
# passing the value of above found out 3D points (threedpoints)
# and its corresponding pixel coordinates of the
# detected corners (twodpoints)
ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
    threedpoints, twodpoints, grayColor.shape[::-1], None, None)
 
 
# Load a test image
test_img = '/home/mauricio/basler_calibration/A.tiff'
test_img = cv2.imread(test_img)
grayColor = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)

h,  w = grayColor.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(matrix, distortion, (w,h), 1, (w,h))

dst = cv2.undistort(grayColor, matrix, distortion, None, newcameramtx)
# crop the image
x, y, w, h = roi
print(roi)
#dst = dst[y:y+h, x:x+w]

cv2.imshow('img',dst)
cv2.waitKey(0)