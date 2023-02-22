
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.animation import FuncAnimation
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

class PlotWidget(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)
        
        self.frames = []
        self.h = []
        self.H = []
        
        # Widgets
        self.pltCanvas = FigureCanvas()
        self.pltToolbar = NavigationToolbar(self.pltCanvas)
        
        # Init routines
        self.axs = self.pltCanvas.figure.gca()
        self.animation = FuncAnimation(self.pltCanvas.figure, self.update_plot)
        self.animation.pause()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.pltToolbar)
        layout.addWidget(self.pltCanvas)

        self.setLayout(layout)

    def update(self, values):
        frame, h, H = values
        # Clean axis
        self.frames.append(frame)
        self.h.append(h)
        self.H.append(H)


    def update_plot(self, i):
        self.axs.cla()
        self.axs.plot(self.frames, self.h)
        self.axs.plot(self.frames, self.H)


if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = PlotWidget()
    widget.show()
    sys.exit(app.exec_())
