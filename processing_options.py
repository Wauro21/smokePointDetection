import argparse

# Default values
DEFAULT_CORE_THRESHOLD=35.0
DEFAULT_CONTOUR_THRESHOLD = 2.5
DEFAULT_DERIVATIVE_THRESHOLD= 2e-5


class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __eq__(self, other):
        return self.start <= other <= self.end

def argsHandler():
        # [FIX]: Change the description of the algorithm
        dsc = "Implements the algorithm described in the paper"
        parser = argparse.ArgumentParser(description=dsc)
        parser.add_argument("-i", "--Input", required=True, help="Input video or image folder to process")
        # [FIX]: Add image processing, like external frames
        parser.add_argument("-d", "--Display", action='store_true', help="Displays the processing process")
        parser.add_argument("-tcore", "--ThresholdCore", default=DEFAULT_CORE_THRESHOLD, type=float, help="Percentage of the max value to use as threshold for the core region. Default is {}".format(DEFAULT_CORE_THRESHOLD))
        parser.add_argument("-tcontour", "--ThresholdContour", default=DEFAULT_CONTOUR_THRESHOLD, type=float, help="Percentage of the max value to use as threshold for the contour region. Default is {}".format(DEFAULT_CONTOUR_THRESHOLD))
        parser.add_argument("-dt", "--DerivativeThreshold", help='Lower bound for finding linear region. By default is {}'.format(DEFAULT_DERIVATIVE_THRESHOLD), type=float, default=DEFAULT_CORE_THRESHOLD)
        parser.add_argument("-bb","--Boxes", help="Shows bounding boxes for the regions", action='store_true')
        parser.add_argument("-sv","--SaveValues", help="Generates a file, saving the estimated height values, the coefficientes of the polynoms and the resulting plots")
        parser.add_argument("-mm", help= "Uses the px to mm convertion for thes calculations", action='store_true')
        parser.add_argument("--Verbose", action='store_true', help='If passed enables information prints through terminal.')
        args = parser.parse_args()
        return args

if __name__ == '__main__':
    args = argsHandler()
    print(args)
