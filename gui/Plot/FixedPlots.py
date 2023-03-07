import math
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from GUI_CONSTANTS import PLOT_HEIGHT_POLY_DOTS_COLOR, PLOT_HEIGHT_POLY_DOTS_LABEL, PLOT_HEIGHT_POLY_LINE_COLOR, PLOT_HEIGHT_POLY_LINE_LABEL, PLOT_HEIGHTS_POLY_XLABEL, PLOT_HEIGHTS_POLY_YLABEL, PLOT_WIDGET_HEIGHT, PLOT_WIDGET_WIDTH


class FixedPlot(QWidget):

    def __init__(self, title,  parent=None):

        super().__init__(parent)

        # Objects
        self.title = title

        # Widgets
        self.fig = Figure()
        self.pltCanvas = FigureCanvas(self.fig)
        self.pltToolbar = NavigationToolbar(self.pltCanvas)

        # init routines
        self.fig.subplots(nrows=1, ncols=1)
        self.axs = self.pltCanvas.figure.gca()
        self.setFixedHeight(PLOT_WIDGET_HEIGHT)
        self.setFixedWidth(PLOT_WIDGET_WIDTH)

        # Signals and Slots

        # layout

        layout = QVBoxLayout()
        layout.addWidget(self.pltToolbar)
        layout.addWidget(self.pltCanvas)
        self.setLayout(layout)

    def getTitle(self):
        return self.title


class PolyHeightPlot(FixedPlot):

    def __init__(self, title, parent=None):

        super().__init__(title, parent)
        # Set labels
        self.axs.set_xlabel(PLOT_HEIGHTS_POLY_XLABEL)
        self.axs.set_ylabel(PLOT_HEIGHTS_POLY_YLABEL)
        self.axs.grid()


    def plot(self, process_controls):
        # Raw data
        h = process_controls['h']
        H = process_controls['H']
        poly_coef = process_controls['10th_poly']

        # Polynomial bounds
        h_min = math.floor(min(h))
        h_max = math.ceil(max(h))
        samples = len(h)
        poly_h = np.linspace(h_min, h_max, samples)
        poly_values = np.polyval(poly_coef, poly_h)

        # Plot 
        self.axs.scatter(h, H, color=PLOT_HEIGHT_POLY_DOTS_COLOR, label=PLOT_HEIGHT_POLY_DOTS_LABEL)
        self.axs.plot(poly_h, poly_values, color=PLOT_HEIGHT_POLY_LINE_COLOR, label=PLOT_HEIGHT_POLY_LINE_LABEL)

        # Set the legend 
        self.axs.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=4)
        # Draw on canva
        self.pltCanvas.draw()

