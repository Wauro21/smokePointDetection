import cv2
import numpy as np

path = '/mnt/shared/SP_18_08_22/sp_test_30fps_1/Basler_acA2040-55uc__23734412__20220818_183353703_0000.tiff'
cv2.namedWindow('Input', cv2.WINDOW_NORMAL)
cv2.namedWindow('HED', cv2.WINDOW_NORMAL)

img = cv2.imread(path)


gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

sobel_y = cv2.Sobel(gray_frame, cv2.CV_64F, 1, 0, ksize=3)
sobel_x = cv2.Sobel(gray_frame, cv2.CV_64F, 0, 1, ksize=3)

abs_grad_x = cv2.convertScaleAbs(sobel_x)
abs_grad_y = cv2.convertScaleAbs(sobel_y)
grad = cv2.addWeighted(abs_grad_x, 0.1, abs_grad_y, 0.9, 0)

result = cv2.addWeighted(gray_frame, 1, grad, -1,0)
borders = cv2.addWeighted(gray_frame, 1, result, -1,0)



test = np.zeros_like(img)
test[:,:,0] = borders
test[:,:,1] = borders
test[:,:,2] = borders

img_hed = img

(H, W) = img_hed.shape[:2]
blob = cv2.dnn.blobFromImage(img_hed, scalefactor=1.0, size=(W, H),
    swapRB=False, crop=False)
net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "hed_pretrained_bsds.caffemodel")
net.setInput(blob)
hed = net.forward()
hed = cv2.resize(hed[0, 0], (W, H))
hed = (255 * hed).astype("uint8")
cv2.imshow("Input", img)
cv2.imshow("HED", hed)
while(1):
    if cv2.waitKey(1) == ord('q'):
        break