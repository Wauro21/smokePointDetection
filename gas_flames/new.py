import cv2
import os
import numpy as np


folder_to_process = '/mnt/shared/SP_18_08_22/sp_test_30fps_1/Basler_acA2040-55uc__23734412__20220818_183353703_%04d.tiff'

media = cv2.VideoCapture(folder_to_process)
n_frames = int(media.get(cv2.CAP_PROP_FRAME_COUNT))
width  = int(media.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(media.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
out = cv2.VideoWriter('testing_ai.mp4', fourcc, 30, (width, height))

# cv2.namedWindow('Sobel_Y', cv2.WINDOW_NORMAL)
# cv2.namedWindow('Sobel_X', cv2.WINDOW_NORMAL)
# cv2.namedWindow('Original', cv2.WINDOW_NORMAL)
# cv2.namedWindow('Grad', cv2.WINDOW_NORMAL)
# cv2.namedWindow('Sum', cv2.WINDOW_NORMAL)
# cv2.namedWindow('TEST', cv2.WINDOW_NORMAL)

cords = (0,50)
font= cv2.FONT_HERSHEY_SIMPLEX
fontScale = 1
color = (255,0,255)
thickness = 2

count = 0
display_text = '{}/{}'


while media.isOpened():
    
    ret,frame = media.read()
    if not ret:
        break

    count += 1
    
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('original.tiff', frame)
    # cv2.imwrite('gray.tiff', gray_frame)

    sobel_y = cv2.Sobel(gray_frame, cv2.CV_64F, 1, 0, ksize=3)
    sobel_x = cv2.Sobel(gray_frame, cv2.CV_64F, 0, 1, ksize=3)

    abs_grad_x = cv2.convertScaleAbs(sobel_x)
    abs_grad_y = cv2.convertScaleAbs(sobel_y)

    grad = cv2.addWeighted(abs_grad_x, 0.1, abs_grad_y, 0.9, 0)

    # cv2.imwrite('grad.tiff', grad)
    
    result = cv2.addWeighted(gray_frame, 1, grad, -1,0)
    borders = cv2.addWeighted(gray_frame, 1, result, -1,0)

    cv2.imwrite('test/{:04d}.tiff'.format(count), result)
    # cv2.imwrite('borders.tiff', borders)

    test = cv2.addWeighted(gray_frame,-1, grad, 1,0)
    # cv2.imwrite('pre_inv_borders.tiff', test)

    frame_text = cv2.putText(result, display_text.format(count, n_frames), cords, font, fontScale, color, thickness, cv2.LINE_AA)

    out.write(frame_text)

    # cv2.imshow('Sobel_Y', sobel_y)
    # cv2.imshow('Original', frame_text)
    # cv2.imshow('Sobel_X', sobel_x)
    # cv2.imshow('Grad', grad)
    # cv2.imshow('Sum', borders)
    # cv2.imshow('TEST', test)

    
    # if cv2.waitKey(1) == ord('q'):
    #     break
