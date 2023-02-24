
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.animation import FuncAnimation
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from GUI_CONSTANTS import PLOT_WIDGET_HEIGHT, PLOT_WIDGET_TRACE_A_COLOR, PLOT_WIDGET_TRACE_B_COLOR, PLOT_WIDGET_WIDTH

class PlotWidget(QWidget):

    def __init__(self, title,x_axis, y_axis, legend_labels, parent=None):

        super().__init__(parent)
        
        # -> Values
        self.x = []
        self.y = []
        self.z = []
        
        # -> Titles
        self.title = title
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.labels = legend_labels
        self.colors = [PLOT_WIDGET_TRACE_A_COLOR, PLOT_WIDGET_TRACE_B_COLOR]
        
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


    def setColors(self, colors):
        self.colors = colors

    def getTitle(self):
        return self.title

    def restoreAx(self):
        self.axs.cla()
        self.axs.grid()
        self.axs.set_title(self.title)
        self.axs.set_xlabel(self.x_axis)
        self.axs.set_ylabel(self.y_axis)

    def update(self, values):
        x, y, z = values
        
        self.x.append(x)
        self.y.append(y)
        self.z.append(z)


    def update_plot(self, i):
        self.restoreAx()
        y = self.axs.plot(self.x, self.y, label=self.labels[0], color=self.colors[0])
        z = self.axs.plot(self.x, self.z, label=self.labels[1], color=self.colors[1])

        #handles, labels = self.axs.get_legend_handles_labels()
        #self.pltCanvas.figure.legend(handles, labels, loc=1)


if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = PlotWidget()
    widget.show()
    sys.exit(app.exec_())
