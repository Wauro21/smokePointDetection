import cv2 
import numpy as np
import argparse
from utils import dataLoader
from matplotlib import pyplot as plt
import csv
import os
from progress.bar import Bar

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
    
    save_histos = [1, n_frames//2, n_frames]

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

    plt.plot(general_histo)
    plt.grid()
    plt.xlim([0,255])
    plt.xlabel('Bins')
    plt.ylabel('Pixeles')
    plt.title('Average histogram analysis')
    plt.savefig(os.path.join(args.of, 'average_histogram.pdf'))

    # Zoom view
    bin_start = 1
    bin_end = -1
        
    for i,bin in enumerate(general_histo):
        if(bin[0] == 0):
            bin_end = i
            break
    plt.xlim([bin_start, bin_end])
    plt.ylim([0, general_histo[bin_start][0]])        
    plt.savefig(os.path.join(args.of, '_average_zoom.pdf'))
    plt.show()

    
    if(save_file):
        save_file.close()

    bar.finish()






if __name__ == '__main__':
    args = argHandler()
    histo(args)