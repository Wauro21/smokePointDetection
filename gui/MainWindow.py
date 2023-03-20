from PySide2.QtWidgets import QApplication, QMainWindow
from gui.CentralWidget import CentralWidget
from gui.GUI_CONSTANTS import MAIN_WINDOW_TITLE
import sys
import os

class SPDMain(QMainWindow):
    def __init__(self, parent=None):

        super().__init__(parent)

        # objects

        # widgets
        self.SPD_Widget = CentralWidget(self)

        # init routines
        self.setWindowTitle(MAIN_WINDOW_TITLE)
        self.setCentralWidget(self.SPD_Widget)

        # signals and slots

        # layout


if __name__ == '__main__':

    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    window = SPDMain()
    window.show()
    sys.exit(app.exec())
