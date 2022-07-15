import argparse

def argsHandler():
        # [FIX]: Change the description of the algorithm
        dsc = "Implements the algorithm described in the paper"
        parser = argparse.ArgumentParser(description=dsc)
        parser.add_argument("-v", "--Video", help="Input video to process")
        # [FIX]: Add image processing, like external frames
        parser.add_argument("-d", "--Display", action='store_true', help="Displays the processing process")
        parser.add_argument("-tcore", "--TresholdCore", help="Percentage of the max value to use as threshold for the core region")
        parser.add_argument("-tcontour", "--TresholdContour", help="Percentage of the max value to use as threshold for the contour region")
        parser.add_argument("-bb","--Boxes", help="Shows bounding boxes for the regions", action='store_true')
        parser.add_argument("-sv","--SaveValues", help="Generates a file, saving the estimated height values, the coefficientes of the polynoms and the resulting plots")
        parser.add_argument("-mm", help= "Uses the px to mm convertion for thes calculations", action='store_true')
        args = parser.parse_args()
        return args

if __name__ == '__main__':
    args = argsHandler()
    print(args)
