# Main handler for GUI/terminal calls
import sys
import os
from PyQt5.QtWidgets import QApplication
from core.processing import smokepoint
from core.processing_options import argsHandler
from gui.MainWindow import SPDMain
from gui.utils import resultPlotting



def CMDsp(args):
    sp_vals = smokepoint(args)
    print('Invalid Frames : {}'.format(sp_vals['n_invalid_frames']))
    resultPlotting(sp_vals,True)




if __name__ == '__main__':

    args = argsHandler()

    if(args.cmd):
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