import cv2 
import numpy as np
import argparse
from utils import dataLoader
from matplotlib import pyplot as plt
import csv
import os
from progress.bar import Bar
import matplotlib
matplotlib.use('tkAgg')

def argHandler():
    dsc='Histogram analysis of the input image'
    parser = argparse.ArgumentParser(description=dsc)
    parser.add_argument('-i',help='Input image')
    parser.add_argument('-of', help='Output folder of the analysis',required=True)
    parser.add_argument("-cut", help="Cut the frames columnwise from center axis", type=int)
    parser.add_argument('-save', help='Saves the resulting data to file', type=str)
    args = parser.parse_args()
    return args

def histo(args):
    # Save path
    if not (os.path.isdir(args.of)):
        print('Folder does not exists')
    
    save_file = None
    writer = None
    if (args.save):
        save_file = open(os.path.join(args.of, args.save+'_histogram_data.csv'),'w')
        writer = csv.writer(save_file)


    # Histo acumulator
    general_histo = np.zeros([256,1])

    # Load frame/s
    path = dataLoader(args.i)
    media = cv2.VideoCapture(path, 0)
    n_frames = int(media.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(media.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(media.get(cv2.CAP_PROP_FRAME_HEIGHT))
    bar = Bar('Histogram analysis', max=n_frames)
    
    #save_histos = [1, n_frames//2, n_frames]
    save_histos = []
    frame_counter = 0
    while media.isOpened():
        ret, frame = media.read()
        if not ret:
            print('End of frames')
            break
        frame_counter += 1
        if(args.cut):
            cut = args.cut//2
            center_line = width//2
            frame = frame[:,center_line-cut:center_line+cut]

        # Convert to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Get histogram
        frame_histogram = cv2.calcHist([gray_frame], [0],None,[256],[0,256]) 

        # Acumulate results and write to file if needed
        general_histo += frame_histogram

        if(writer):
            writer.writerow(frame_histogram)

        # Plot results 
        if(frame_counter in save_histos):
            # General view
            plt.plot(frame_histogram)
            plt.grid()
            plt.xlim([0,255])
            plt.xlabel('Bins')
            plt.ylabel('Pixeles')
            plt.title('Histogram analysis for {} frame'.format(frame_counter))
            plt.savefig(os.path.join(args.of, '{}_histo.pdf'.format(frame_counter)))

            # Zoom view
            bin_start = 1
            bin_end = -1
        
            for i,bin in enumerate(frame_histogram):
                if(bin[0] == 0):
                    bin_end = i
                    break

            plt.xlim([bin_start, bin_end])
            plt.ylim([0, frame_histogram[bin_start][0]])
            plt.savefig(os.path.join(args.of, '{}_histo_zoom.pdf'.format(frame_counter)))
            plt.clf()
        
        # Progress Bar
        bar.next()

    # Plot general histogram and save values
    general_histo = general_histo/n_frames # To get average 
   
    if(save_file):
        save_file.close()


    flame_pixels = 0
    pivot = 0#5
    regions = {}
    for i, bin in enumerate(range(pivot,256)):
        flame_pixels += general_histo[bin][0]
        regions[i] = flame_pixels

    # Print results 
    print('Total flame pixels {}'.format(flame_pixels))
    prev_value = 0
    delta = 0
    contour_bin = float('-inf')
    contour_pixels = 0
    contour_bin_flag = True
    general_acum = 0
    for key in regions: 
        delta = 100*(regions[key] - prev_value)/flame_pixels
        if(delta < 1.0 and contour_bin_flag):
            contour_bin = key
            contour_bin_flag = False
            contour_pixels = flame_pixels - regions[key]

        prev_value = regions[key]
        print("Bin {} = {} pixels | {} %".format(key+pivot, regions[key], 100*regions[key]/flame_pixels))
    
    
    print("Contour found at: {}".format(contour_bin))
    print('Contour formed with {} pixels'.format(contour_pixels))
    
    # Core
    acum = 0
    core_bin = 0
    for key in regions:
        if(key <= contour_bin):
            continue
        
        acum += regions[key]
        if(acum >= round(30*contour_pixels/100)):
            core_bin = key
            print("Core found at {}".format(key))
            break

    # Plots 
    # -> General histogram - Contour
    fig = plt.figure()
    #fig.set_size_inches(20,11.25)
    plt.plot(general_histo)
    plt.xlabel('Bins')
    plt.ylabel('Pixels')
    plt.title('Average Histogram Analysis')
    #plt.xticks(np.arange(0,255, step=10))
    plt.axvline(x=contour_bin, color='r', linestyle='dashed',label='Contour Threshold {} px'.format(contour_bin))
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(args.of,'contour_histo.pdf'))
    plt.clf()

    # -> Histo zoom to flame-conbtour - core
    plt.plot(general_histo)
    plt.xlabel('Bins')
    plt.ylabel('Pixels')
    plt.title('Average Histogram Analysis')
    #plt.xticks(np.arange(0,255, step=10))
    plt.xlim([contour_bin, 255])
    plt.ylim([0,general_histo[contour_bin]])
    plt.axvline(x=core_bin, color='r', linestyle='dashed',label='Core Threshold {} px'.format(core_bin))
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(args.of,'core_histo.pdf'))
    #plt.show()
    bar.finish()






if __name__ == '__main__':
    args = argHandler()
    histo(args)