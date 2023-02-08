import sys
import os

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from LoadWidget import LoadWidget

__version__ ='0.1'
__author__ = 'maurio.aravena@sansano.usm.cl'

class CentralWidget(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)

        self.prefix = None
        
        # Objects 

        # Widgets
        self.LoadWidget = LoadWidget(self)

        # Init routines

        # Signals and Slots
        self.LoadWidget.prefix_signal.connect(self.setPrefix)

        # Layout
        # -> Demo layout
        layout = QVBoxLayout()
        layout.addWidget(self.LoadWidget)

        self.setLayout(layout)

    def setPrefix(self, prefix):
        self.prefix = prefix



if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = CentralWidget()
    widget.show()
    sys.exit(app.exec_())