
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.animation import FuncAnimation
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from GUI_CONSTANTS import PLOT_WIDGET_HEIGHT, PLOT_WIDGET_TRACE_CONTOUR, PLOT_WIDGET_TRACE_CORE, PLOT_WIDGET_TRACE_TIP, PLOT_WIDGET_WIDTH

class ProcessPlotWidget(QWidget):

    def __init__(self, title,x_axis, y_axis, legend_labels, parent=None):

        super().__init__(parent)
        
        # -> Values
        self.frames = []
        self.contour = []
        self.core = []
        self.tip = []
        
        # -> Titles
        self.title = title
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.labels = legend_labels
        
        # Widgets
        self.pltCanvas = FigureCanvas()
        self.pltToolbar = NavigationToolbar(self.pltCanvas)
        
        # Init routines
        self.setFixedHeight(PLOT_WIDGET_HEIGHT)
        self.setFixedWidth(PLOT_WIDGET_WIDTH)
        self.axs = self.pltCanvas.figure.gca()
        self.animation = FuncAnimation(self.pltCanvas.figure, self.update_plot)
        self.animation.pause()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.pltToolbar)
        layout.addWidget(self.pltCanvas)

        self.setLayout(layout)

    def getTitle(self):
        return self.title

    def restoreAx(self):
        self.axs.cla()
        self.axs.grid()
        #self.axs.set_title(self.title)
        self.axs.set_xlabel(self.x_axis)
        self.axs.set_ylabel(self.y_axis)

    def update(self, values):
        frames, contour, tip = values
        
        self.frames.append(frames)
        self.contour.append(contour)
        self.tip.append(tip)
        self.core.append(contour - tip)


    def update_plot(self, i):
        self.restoreAx()
        # Plot contour height
        self.axs.plot(self.frames, self.contour, label=self.labels[0], color=PLOT_WIDGET_TRACE_CONTOUR)
        # Plot core height
        self.axs.plot(self.frames, self.core, label=self.labels[1], color=PLOT_WIDGET_TRACE_CORE)
        # Plot tip 
        self.axs.plot(self.frames, self.tip, label=self.labels[2], color=PLOT_WIDGET_TRACE_TIP)
        
        self.axs.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=3)


if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = PlotWidget()
    widget.show()
    sys.exit(app.exec_())
