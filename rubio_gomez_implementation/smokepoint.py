import cv2 as cv2
import numpy as np
import glob
import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import signal
import pwlf
import time

parser = argparse.ArgumentParser()
groupInput = parser.add_mutually_exclusive_group(required=True)
groupInput.add_argument("-v", "--video", help="path to video")
groupInput.add_argument("-i", "--images", help="path to directory containing images (the names have to be sorted alphabetically)")
parser.add_argument("-t", "--threshold", type=int, default=230, help="threshold to separate foreground and background")
parser.add_argument("-r", "--widthratio", type=float, default=0.4, help="tipWidth = flameWidth * widthRatio")
parser.add_argument("-d", "--display", action='store_true', help="If used, displays flame")
parser.add_argument("-o", "--output", default='smokePoint', help="Name of output plot")

mpl.use("pgf")
# bbox format: [x, y, w, h]

def get_mask(image, threshold):
    try:
        # if image has 3 channels (assumed to be rgb), convert to grayscale
        if image.ndim == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # if image has 1 channel it is assumed that its in grayscale 
        elif image.ndim == 2:
            gray = image
        else:
            raise NameError('Wrong number of channels')
    except NameError:
        print("Image has a number of channels different than 1 or 3")

    _, mask = cv2.threshold(gray, thresh=threshold, maxval=255, type=cv2.THRESH_BINARY)
    #_, mask2 = cv2.threshold(gray, thresh=threshold, maxval=255, type=cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    #cv2.imshow("normal th", cv2.WINDOW_NORMAL)
    #cv2.imshow("otsu th", cv2.WINDOW_NORMAL)    
    #cv2.imshow("normal th", mask)
    #cv2.imshow("otsu th", mask2)
    #cv2.waitKey(1)
    # find blobs
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    # search for blob with largest area
    areas = stats[1:,cv2.CC_STAT_AREA]
    imax = max(enumerate(areas), key=(lambda x: x[1]))[0] + 1
    bbox = [stats[imax, cv2.CC_STAT_LEFT],
            stats[imax, cv2.CC_STAT_TOP], 
            stats[imax, cv2.CC_STAT_WIDTH], 
            stats[imax, cv2.CC_STAT_HEIGHT]]
    # mask of largest blob
    mask = np.uint8(labels==imax)*255
    return mask, bbox

def get_ratio(mask, widthRatio): 
    # input mask must be cropped arround the flame!
    flameWidth = mask.shape[1]
    flameHeight = mask.shape[0]

    tipWidth = flameWidth * widthRatio
    tipHeight = 0
    x_offset = 0

    # find tip height from top to bottom
    for row in range(flameHeight):
        width = np.sum(mask[row, :])/255.0
        if width >= tipWidth:
            tipHeight = row
            tipWidth = width
            # get horizontal offset
            x_offset = np.where(mask[row, :] == 255)[0][0]
            break

    return tipWidth, tipHeight, flameWidth, flameHeight, x_offset

def draw_bbox(img, bbox, color, width):
    bbox = [int(i) for i in bbox]
    left , top = bbox[0], bbox[1]
    right, bottom = bbox[0]+bbox[2], bbox[1]+bbox[3]
    cv2.rectangle(img, (left , top), (right, bottom), color, width)
    return img

def sort_arrays(array1, array2): 
    # sorts array1 keeping correspondence with array2 
    zipped_pairs = zip(array1, array2) 
    array2 = [x for _, x in sorted(zipped_pairs)] 
    array1 = sorted(array1)  
    return array1, array2

def main(video, path, threshold, widthRatio, outputName, display):

    filtWindow = [.04, .08, .12, .16, .2, .16, .12, .08, .04]
    tipRatioArray = np.array([])
    tipHeightarray = np.array([])

    if display:
        cv2.namedWindow("input", cv2.WINDOW_NORMAL)
        cv2.namedWindow("mask", cv2.WINDOW_NORMAL)

    if video:
        cap = cap = cv2.VideoCapture(path)
    else:
        image_list = sorted(glob.glob(path+"/*"))

    #t1 = time.clock()
    #t2 = time.clock()
    while(True):
        #t2 = t1
        #t1 = time.clock()
        #fps = round(1/(t1 - t2),3)

        #print(fps)
        if video:
            # get new img    
            retval, img = cap.read()
            # end loop
            if not retval:
                break
        else:
            # end loop
            if not image_list:
                break
            # read from image
            img = cv2.imread(image_list.pop(0))
        
        mask, bbox = get_mask(img, threshold)
        croppedMask = mask[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]
        tipWidth, tipHeight, flameWidth, flameHeight, x_offset = get_ratio(croppedMask, widthRatio)
        bboxTip = [bbox[0]+x_offset, bbox[1], tipWidth, tipHeight]

        tipRatio = tipHeight/tipWidth
        tipRatioArray = np.append(tipRatioArray, tipRatio)
        tipHeightarray = np.append(tipHeightarray, flameHeight)

        if display:
            draw_bbox(img, bbox, (0,255,0), 2)
            draw_bbox(img, bboxTip, (0,0,255), 2)
            tipRatioTxt = "Tip Ratio: {}".format(round(tipRatio,3))
            tipWidthTxt = "Tip Width: {}".format(round(tipWidth,3))
            tipHeightTxt = "Tip Height: {}".format(round(tipHeight,3))
            #fpsTxt = "Fps: {}".format(fps)
            #cv2.putText(img, fpsTxt,(10,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv2.LINE_AA)
            cv2.putText(img, tipRatioTxt,(10,90), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv2.LINE_AA)
            cv2.putText(img, tipWidthTxt,(10,130), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv2.LINE_AA)
            cv2.putText(img, tipHeightTxt,(10,170), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv2.LINE_AA)
            
            cv2.imshow("input", img)
            cv2.imshow("mask", mask)
            cv2.waitKey(1)


    tipHeightarray, tipRatioArray = sort_arrays(tipHeightarray, tipRatioArray)

    # filter signal with average window
    tipRatioArray = signal.convolve(tipRatioArray, filtWindow, mode='same')

    # initialize piecewise linear fit
    my_pwlf = pwlf.PiecewiseLinFit(tipHeightarray[:5000], tipRatioArray[:5000])
    #my_pwlf = pwlf.PiecewiseLinFit(tipHeightarray, tipRatioArray)
    
    # fit the data for two line segments
    breakPoints = my_pwlf.fit(2)
    # predict for the determined points
    xHat = np.linspace(min(tipHeightarray), max(tipHeightarray), num=10000)
    yHat = my_pwlf.predict(xHat)

    # Second breakPoint is were the two lines intersect
    smokePoint = breakPoints[1]

    # use LaTeX fonts in the plot
    #plt.rc('text', usetex=True)
    #plt.rc('font', family='serif')
    plt.plot(tipHeightarray, tipRatioArray, 'o', xHat, yHat, '--')
    plt.title('Smoke Point r= {} th= {}'.format(widthRatio, threshold))
    plt.axvline(x=smokePoint, linewidth=1, color='c')
    ymin, xmax = plt.gca().get_ylim()
    plt.annotate('Smoke Point Height: ' + str(round(smokePoint)), xy=(smokePoint, ymin), xytext=(smokePoint + 100, ymin + 0.2),
            arrowprops=dict(facecolor='black', shrink=0.05))
    plt.xlabel('Flame height [pixels]')
    plt.ylabel('Flame tip ratio (tip height)/(tip width)')
    #plt.show()
    plt.savefig(outputName + '.pgf')
    plt.savefig(outputName + '.pdf')

    return 0

if __name__ == "__main__":
    args = parser.parse_args()
    threshold = args.threshold
    widthRatio = args.widthratio
    display = args.display
    outputName = args.output
    
    if args.video:
        print("video input")
        main(True, args.video, threshold, widthRatio, outputName, display)
    elif args.images:
        print("images input")
        main(False, args.images, threshold, widthRatio, outputName, display)