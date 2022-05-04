import cv2 as cv2
import numpy as np
import argparse
from matplotlib import pyplot as plt
from progress.bar import Bar # Util for displaying progress through terminal
import csv

# Default values
MAX_PIXEL_VALUE = 255
CORE_THRESHOLD_PERCENT = 0.75
CONTOUR_THRESHOLD_PERCENT = 0.35
MAX_CENTROID_TOLERANCE = 50.0
DERIVATIVE_COMP = 2e-5
# -> Convertion values
M_PX_CM = 0.1038
C_PX_CM = 3.55

class FlameEstimator:
    def __init__(self):
        self.h_px = []
        self.H_px = []
        self.h_mm = []
        self.H_mm = []

def save2File(fields, rows, outfile, print):
    with open(outfile, 'w') as file:
        write = csv.writer(file)
        write.writerow(fields)
        write.writerow(rows)
    if(print):
        print("[INFO] outfile was saved!")


def px2mm(input_value):
    d = (M_PX_CM*input_value) + C_PX_CM
    return d
def write2Frame(input_frame, pos, scale, color, thick,text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    return_frame = cv2.putText(input_frame, text, pos, font, scale, color, thick, cv2.LINE_AA)
    return return_frame

# Revisit this
def getConnectedComponents(threshold_image, connect, display_process):
    cc = cv2.connectedComponentsWithStats(threshold_image, connect, cv2.CV_32S)
    # Unpack de information
    n_labels, labels, stats, centroids = cc
    # Range from 1 to n_labels to disregard background
    return_dict = {
        'x':0,
        'y':0,
        'w':0,
        'h':0,
        'area':-1,
        'cX':0,
        'cY':0,
        'cmask':None
    }

    for i in range(1,n_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if(area > return_dict['area']):
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            (cX,cY) = centroids[i]
            component_mask = (labels==i).astype("uint8")*255
            return_dict = {
                'x':x,
                'y':y,
                'w':w,
                'h':h,
                'area':area,
                'cX':cX,
                'cY':cY,
                'cmask':component_mask
            }
            if(display_process):
                display_cc = threshold_image.copy()
                display_cc = cv2.cvtColor(display_cc, cv2.COLOR_GRAY2BGR)
                cv2.rectangle(display_cc, (x,y), (x+w, y+h), (0,255,0),3)
                cv2.circle(display_cc, (int(cX), int(cY)), 4, (0,0,255),-1)
                cv2.namedWindow("CC+Stats", cv2.WINDOW_NORMAL)
                cv2.namedWindow("CC", cv2.WINDOW_NORMAL)
                cv2.imshow("CC+Stats", display_cc)
                cv2.imshow("CC", component_mask)
                cv2.waitKey(0)
    return return_dict



def main():
    # [FIX]: Change the description of the algorithm
    dsc = "Implements the algorithm described in the paper"
    parser = argparse.ArgumentParser(description=dsc)
    parser.add_argument("-v", "--Video", help="Input video to process")
    # [FIX]: Add image processing, like external frames
    parser.add_argument("-d", "--Display", action='store_true', help="Displays the processing process")
    parser.add_argument("-tcore", "--TresholdCore", help="Percentage of the max value to use as threshold for the core region")
    parser.add_argument("-tcontour", "--TresholdContour", help="Percentage of the max value to use as threshold for the contour region")
    parser.add_argument("-bb","--Boxes", help="Shows bounding boxes for the regions", action='store_true')
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
            # Extract number of frames for progress bar
            n_frames = int(vid.get(cv2. CAP_PROP_FRAME_COUNT))
        except cv2.error as e:
            print("[ERROR] Video couldn't be opened or found!")
    else:
        print("[WARNING] No input video was given! Ending program.")
        exit(1)

    # [FIX]: Find a better way to display the frames
    if(args.Display):
        cv2.namedWindow("input", cv2.WINDOW_NORMAL)

    # Playing video frame by frame to process.
    reference_cX = None
    first_frame = True
    values = FlameEstimator()
    invalid_frames = 0
    # Generating a progress bar
    bar = Bar('Processing', max=n_frames)
    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            print("[INFO] End of stream, processing is done")
            break
        else:
            # 1 - Convert input to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 2 - Umbralize
            t_core_ret, core_t = cv2.threshold(gray_frame,CORE_THRESHOLD, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
            t_contour_ret, contour_t = cv2.threshold(gray_frame, CONTOUR_THRESHOLD, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)

            # 3 - Height: From connected components get the info
            core_components = getConnectedComponents(core_t, 4, False)
            contour_components = getConnectedComponents(contour_t, 4, False)

            contour_height = contour_components['h']
            contour_height_mm = px2mm(contour_height)
            # For this operation, consider that (0,0) is top left corner
            tip_height =  core_components['y'] -contour_components['y']
            tip_height_mm = px2mm(tip_height)
            # If needed, show bounding boxes for core and countour
            if(args.Boxes):
                cv2.rectangle(frame, (contour_components['x'],contour_components['y']), (contour_components['x']+contour_components['w'], contour_components['y']+contour_components['h']), (0,255,0),3)
                cv2.rectangle(frame, (core_components['x'],core_components['y']), (core_components['x']+core_components['w'], core_components['y']+core_components['h']), (0,0,255),3)
            # write info to frame
            info_text = "h: {} px H: {} px".format(contour_height, tip_height)
            frame_info = write2Frame(frame, (50,50), 1, (0,255,0),2, info_text)
            info_text = "h: {:.2f} mm H: {:.2f} mm".format(contour_height_mm, tip_height_mm)
            frame_info = write2Frame(frame, (50,100), 1, (0,255,0),2, info_text)
            # --> Save the first frame centroid
            if(first_frame):
                reference_cX = contour_components["cX"]
                first_frame = False
            else:
                centroid_diff = abs(contour_components["cX"] -  reference_cX)
                if(centroid_diff <= MAX_CENTROID_TOLERANCE):
                    values.h_px.append(contour_height)
                    values.H_px.append(tip_height)
                    values.h_mm.append(contour_height_mm)
                    values.H_mm.append(tip_height_mm)
                else:
                    invalid_frames += 1

            invalid_text = "N# invalid frames: {}".format(invalid_frames)
            frame_info = write2Frame(frame_info, (50,150),1,(0,0,255),2,invalid_text)
            if(args.Display):
                cv2.imshow("input", frame_info)
                if cv2.waitKey(1) == ord('q'):
                    break
            bar.next()
    bar.finish()
    vid.release()
    if(args.Display):
        cv2.destroyAllWindows()

        # Debuging plots
    plt.plot(values.h_mm, values.H_mm)
    plt.xlabel('Flame Height (Contour Height) mm')
    plt.ylabel('Flame Tip Height (Contour - Core) mm')
    plt.show()
    # 4. Process results
    # Fit poly
    tenth_poly = np.polyfit(values.h_mm, values.H_mm,10)
    der_tenth_poly = np.polyder(tenth_poly,2)
    for flame_height in values.h_mm:
        eval = abs(np.polyval(der_tenth_poly,flame_height))
        if(eval <= DERIVATIVE_COMP):
            print("SMOKE POINT AT {} mm".format(flame_height))
            break

    return 0


if __name__ == "__main__":
    main()
