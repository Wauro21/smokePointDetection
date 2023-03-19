import argparse
import datetime
import sys
from core.CONSTANTS import DEFAULT_CONTOUR_THRESHOLD, DEFAULT_CORE_THRESHOLD, DEFAULT_DERIVATIVE_THRESHOLD, MAX_CENTROID_TOLERANCE, MAX_PIXEL_VALUE


def folderName():
    date = datetime.datetime.now()
    date = date.strftime('%d-%m-%Y_%H-%M-%S')
    f_name = '{}_run'.format(date)
    return f_name

def pixel2percentage(value):
     return round(100*value/MAX_PIXEL_VALUE)

class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __eq__(self, other):
        return self.start <= other <= self.end

def argsHandler():
        dsc = "Smoke Point Detection (SPD) is a python-based software that implements an algorithm that allows to perform smoke point characterization of fuel blends tested on the ASTM-D1322 Standarized Lamps. The software uses images taken during the lamp tests and allows to automatically detect the smoke point."
        parser = argparse.ArgumentParser(description=dsc)
        parser.add_argument("-cmd", action='store_true', help="Only terminal mode enabled. In GUI mode, none of the other arguments are used")
        parser.add_argument("-i", "--Input", required='-cmd' in sys.argv, help="Input video or image folder to process")
        parser.add_argument('-config', help='Loads configurations for threshold (core, contour and derivative), frame cutting information, centroid tolerance and px2mm conversion from a json file.')
        parser.add_argument("-core", "--ThresholdCore", default=pixel2percentage(DEFAULT_CORE_THRESHOLD), type=float, help="Percentage of the max value to use as threshold for the core region. Default is {}%%".format(pixel2percentage(DEFAULT_CORE_THRESHOLD)))
        parser.add_argument("-contour", "--ThresholdContour", default=pixel2percentage(DEFAULT_CONTOUR_THRESHOLD), type=float, help="Percentage of the max value to use as threshold for the contour region. Default is {}%%".format(pixel2percentage(DEFAULT_CONTOUR_THRESHOLD)))
        parser.add_argument("-dt", "--DerivativeThreshold", help='Lower bound for finding linear region. By default is {}'.format(DEFAULT_DERIVATIVE_THRESHOLD), type=float, default=DEFAULT_DERIVATIVE_THRESHOLD)
        parser.add_argument("-ct", "--CentroidTolerance", help='Centroid tolerance for discarting frames. By default is {}'.format(MAX_CENTROID_TOLERANCE), type=int, default=MAX_CENTROID_TOLERANCE)
        parser.add_argument("-sv","--SaveValues", help="", nargs='?', const=folderName()) # FILL THE HELP FILED
        parser.add_argument("-mm", help= "A conversion factor from px to mm can provided")
        parser.add_argument("-cut", nargs='+', help="Cut the frames columnwise from center axis")
        parser.add_argument("--Verbose", action='store_true', help='If passed enables information prints through terminal.')
        args = parser.parse_args()
        return args

if __name__ == '__main__':
    args = argsHandler()
    print(args)
