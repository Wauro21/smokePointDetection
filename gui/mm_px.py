import cv2
from utils import getConnectedComponents
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.patches as patches
#from PIL import Image
import numpy as np

internal_corners = 4

check_img = '/home/mauricio/Downloads/A.tiff'
#cv2.namedWindow('view', cv2.WINDOW_NORMAL)
img = cv2.imread(check_img)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY_INV)

ret, corners = cv2.findChessboardCornersSB(gray, (internal_corners, internal_corners))

sides = {}
plt.imshow(img)
recs = []
for i in range(internal_corners-1):
    for j in range(internal_corners-1):

        # Get vertices

        x_1 = corners[i*internal_corners+j][0][0]
        y_1 = corners[i*internal_corners+j][0][1]

        x_2 = corners[i*internal_corners+j+1][0][0]
        y_2 = corners[i*internal_corners+j+1][0][1]

        x_3 = corners[(i+1)*internal_corners+j][0][0]
        y_3 = corners[(i+1)*internal_corners+j][0][1]

        x_4 = corners[(i+1)*internal_corners+j+1][0][0]
        y_4 = corners[(i+1)*internal_corners+j+1][0][1]

        # Average all the vertices 
        a = x_2 - x_1
        b = y_4 - y_2
        c = x_4 - x_3 
        d = y_3 - y_1
        
        l = (a + b + c + d) // 4

        sides[i,j] = l

        #plt.gca().add_patch(patches.Rectangle((x_1, y_1), l, l))



plt.imshow(img)
plt.scatter(corners[:,:, 0], corners[:,:, 1])


print(np.mean(list(sides.values())))
print(np.std(list(sides.values())))

plt.show()