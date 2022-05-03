import cv2 as cv2
import numpy as np
import argparse
from matplotlib import pyplot as plt

# Default values
MAX_PIXEL_VALUE = 255
CORE_THRESHOLD_PERCENT = 0.35
CONTOUR_THRESHOLD_PERCENT = 0.75



def main():
    # [FIX]: Change the description of the algorithm
    dsc = "Implements the algorithm described in the paper"
    parser = argparse.ArgumentParser(description=dsc)
    parser.add_argument("-v", "--Video", help="Input video to process")
    # [FIX]: Add image processing, like external frames
    parser.add_argument("-d", "--Display", action='store_true', help="Displays the processing process")
    parser.add_argument("-tcore", "--TresholdCore", help="% of the max value to use as threshold for the core region")
    parser.add_argument("-tcontour", "--TresholdContour", help="% of the max value to use as threshold for the contour region")
    args = parser.parse_args()

    # Set Threshold values
    # - Redefine core's threshold
    if(args.TresholdCore):
        try:
            core_percent = float(args.TresholdCore)/100
        except ValueError:
            print("[ERROR] Couldn't convert value to float. Core's threshold value may be invalid!")
            exit(1)
    else:
        core_percent = CORE_THRESHOLD_PERCENT
    CORE_THRESHOLD = round(MAX_PIXEL_VALUE*core_percent)
    # - Redefine core's threshold
    if(args.TresholdContour):
        try:
            contour_percent = float(args.TresholdContour)/100
        except ValueError:
            print("[ERROR] Couldn't convert value to float. Contours's threshold value may be invalid!")
            exit(1)
    else:
        contour_percent = CONTOUR_THRESHOLD_PERCENT
    CONTOUR_THRESHOLD = round(MAX_PIXEL_VALUE*CONTOUR_THRESHOLD_PERCENT)

    # Inform the user the values that will be used for thresholding
    print("[INFO] The threshold values are:\n\tCore: {}\n\tContour: {}".format(CORE_THRESHOLD,CONTOUR_THRESHOLD))

    # [FIX]: Add image (batch) processing not only video
    if(args.Video):
        try:
            print("[INFO] Video {} will be processed".format(args.Video))
            vid = cv2.VideoCapture(args.Video)
        except cv2.error as e:
            print("[ERROR] Video couldn't be opened or found!")
    else:
        print("[WARNING] No input video was given! Ending program.")
        exit(1)

    # [FIX]: Find a better way to display the frames
    if(args.Display):
        cv2.namedWindow("input", cv2.WINDOW_NORMAL)
        cv2.namedWindow("core", cv2.WINDOW_NORMAL)
        cv2.namedWindow("contour", cv2.WINDOW_NORMAL)
        cv2.namedWindow("composite", cv2.WINDOW_NORMAL)
        cv2.namedWindow("test", cv2.WINDOW_NORMAL)


    test_counter = 0
    # Playing video frame by frame to process.
    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            print("[INFO] End of stream, processing is done")
            break
        else:
            # 1 - Convert input to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 2 - Umbralizacion : Core 191
            t_core_ret, core_t = cv2.threshold(gray_frame,CORE_THRESHOLD, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
            t_contour_ret, contour_t = cv2.threshold(gray_frame, CONTOUR_THRESHOLD, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)

            # Height
            test = cv2.cvtColor(core_t, cv2.COLOR_GRAY2BGR)
            contours_core, hierarchy_core = cv2.findContours(core_t, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #cv2.drawContours(frame, contours_core, -1, (0,0,255), 5)
            x,y,w,h = cv2.boundingRect(contours_core[0])
            cv2.rectangle(test, (x,y),(x+w,y+h), (0,255,0),2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            origin = (50,50)
            fontScale = 1
            color = (0,255,0)
            thickness = 2
            test_text = cv2.putText(test, "Height of BBOX: {} px".format(h), origin, font, fontScale, color, thickness, cv2.LINE_AA)
            cv2.imshow("test", test_text)
            cv2.imwrite("test/sample_frame_{}.png".format(test_counter), test_text)
            test_counter += 1

            cv2.imshow("input", frame)
            cv2.imshow("core", core_t)
            cv2.imshow("contour", contour_t)
            if cv2.waitKey(1) == ord('q'):
                break
    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    main()
