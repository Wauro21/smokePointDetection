import cv2
import os


image_dir = '/mnt/shared/SP_18_08_22/sp_test_30fps_1/Basler_acA2040-55uc__23734412__20220818_183353703_%04d.tiff'


imseq = cv2.VideoCapture(image_dir)
length = int(imseq.get(cv2.CAP_PROP_FRAME_COUNT))
width  = int(imseq.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(imseq.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(imseq.isOpened())
print('frames {}'.format(length))

# cv2.namedWindow('Frames', cv2.WINDOW_NORMAL)



# Frame text
cords = (0,50)
font= cv2.FONT_HERSHEY_SIMPLEX
fontScale = 1
color = (255,0,255)
thickness = 2

count = 0
display = '{}/{}'

fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
out = cv2.VideoWriter('sp_test_30fps_1step.mp4', fourcc, 30, (width, height))

while(imseq.isOpened()):
    ret, frame = imseq.read()
    
    if(ret==True):
        count +=1
        image = cv2.putText(frame, display.format(count, length), cords, font, fontScale, color, thickness, cv2.LINE_AA)
        out.write(image)
        # cv2.imshow('Frames',image)

        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     break
    else:
        break

# imseq.release()