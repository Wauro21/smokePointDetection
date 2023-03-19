# Main handler for GUI/terminal calls
import json
import sys
import os
from PyQt5.QtWidgets import QApplication
from core.processing import smokepoint
from core.processing_options import argsHandler
from gui.MainWindow import SPDMain
from core.utils import resultPlotting


def jsonLoader(args):
    config = args.config

    # Check if file exists 
    if not(os.path.isfile(config)):
        print('File does not exists!')
        exit(1)

    # Load configs
    with open(config, 'r') as json_file:
        try:
            json_dict = json.load(json_file)
            args.ThresholdCore = json_dict['core_%']
            args.ThresholdContour = json_dict['contour_%']
            args.cut = list(json_dict['cut'].values())
            args.mm = json_dict['conv_factor']
            args.DerivativeThreshold = json_dict['der_threshold']
            args.CentroidTolerance = json_dict['centroid_tol']

        except: 
            print('The provided json file is not in the correct format!')
            exit(1)


def CMDsp(args):
    sp_vals = smokepoint(args)
    sp = sp_vals['sp_height']
    print('SP found at {}px'.format(sp))
    if(args.mm):
        mm_val = sp * args.mm
        print('SP found at {} mm'.format(mm_val))
    resultPlotting(sp_vals,True)




if __name__ == '__main__':

    args = argsHandler()
    if(args.cmd):
        # Load config file
        if(args.config):
            jsonLoader(args)
        # Call terminal function
        CMDsp(args)

    else:
        app = QApplication([])
        if os.name == 'nt':
            app.setStyle('Fusion')
        window = SPDMain()
        window.show()
        # For the moment fix the size
        h = window.height()
        w = window.width()
        window.setFixedSize(w, h)
        sys.exit(app.exec())