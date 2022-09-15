import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from utils import getConnectedComponents

matplotlib.use('tkAgg')

cv2.namedWindow('Test', cv2.WINDOW_NORMAL)

img_path = 'pre_borders.png'

img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

inv_img = cv2.bitwise_not(img)



cv2.imwrite('ai_processed_borders.png', inv_img)


ret, thresh = cv2.threshold(inv_img,15,255,cv2.THRESH_BINARY)

cc = getConnectedComponents(thresh, 4)

cv2.imwrite('biggest_cc_border.png', cc['cmask'])

cc_cut = cc['cmask'][:1200,:]

cc_cut = cv2.rotate(cc_cut, cv2.ROTATE_180)

# Get x,y points 

# i -> rows (y axis of image)
# j -> cols (x axis of image)
data = []

for i, row in enumerate(cc_cut):
    for j, col in enumerate(row):
        if(col == 255):
            data.append((j,i))


    

data = np.array(data)

test = dict()
for point in data:
    x,y = point
    if x not in test.keys():
        test[x] = y
    else:
        if y > test[x]:
            test[x] = y

test = dict(sorted(test.items()))

x_data = list(test.keys())
y_data = list(test.values())

plt.scatter(x_data, y_data, c='b')

poly = np.polyfit(x_data, y_data, 10)
poly_val = np.polyval(poly, x_data)

plt.plot(x_data, poly_val, c='r')
plt.show()



cv2.imshow('Test', cc_cut)
# cv2.imshow('Test', cc['cmask'])
cv2.waitKey(0)
cv2.destroyAllWindows()
