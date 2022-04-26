import cv2 as cv2
import numpy as np
import argparse
from matplotlib import pyplot as plt





def main():
    dsc = "Implements the algorithm described in the paper"
    parser = argparse.ArgumentParser(description=dsc)
    parser.add_argument("-v", "--Video", help="Input video")
    parser.add_argument("-d", "--Display", action='store_true', help="Displays output")
    #parser.add_argument("-tc", "--TresholdCore", help="Threshold for the core region")
    # Add values
    args = parser.parse_args()

    # Open video
    if(args.Video):
        try:
            print(args.Video)
            vid = cv2.VideoCapture("test.avi")
        except cv2.error as e:
            print("Video ERROR")
    else:
        print("No inpunt file given")
        exit(1)

    if(args.Display):
        cv2.namedWindow("input", cv2.WINDOW_NORMAL)
        cv2.namedWindow("core", cv2.WINDOW_NORMAL)
        cv2.namedWindow("contour", cv2.WINDOW_NORMAL)
        cv2.namedWindow("composite", cv2.WINDOW_NORMAL)


    # displaying vid - Fix some stuff
    testing = False
    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            print("End of stream")
            break
        else:
            # 1 -Conversion a grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 1 - Umbralizacion : Core 191
            t_core_ret, core_t = cv2.threshold(gray,191, 255, cv2.THRESH_BINARY)
            t_contour_ret, contour_t = cv2.threshold(gray, 89, 255, cv2.THRESH_BINARY)
            if(testing):
                print(core_t.shape)
                print(contour_t.shape)
                cv2.imwrite('sample_input.png', frame)
                cv2.imwrite('sample_core.png', core_t)
                cv2.imwrite('sample_contour.png', contour_t)
                testing = False
            g_channel = np.zeros_like(core_t)
            composite_flame = cv2.merge([contour_t, g_channel, core_t])
            cv2.imshow("input", frame)
            cv2.imshow("core", core_t)
            cv2.imshow("contour", contour_t)
            cv2.imshow("composite", composite_flame)
            if cv2.waitKey(1) == ord('q'):
                break
    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    print("WIP")
    main()
    # Test with image
