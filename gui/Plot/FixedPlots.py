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

from GUI_CONSTANTS import PLOT_HEIGHT_POLY_DOTS_COLOR, PLOT_HEIGHT_POLY_DOTS_LABEL, PLOT_HEIGHT_POLY_LINE_COLOR, PLOT_HEIGHT_POLY_LINE_LABEL, PLOT_HEIGHT_POLY_TITLE_TAB, PLOT_HEIGHTS_POLY_XLABEL, PLOT_HEIGHTS_POLY_YLABEL, PLOT_LINEAR_DER_LABEL, PLOT_LINEAR_REGION_LABEL, PLOT_LINEAR_TITLE_TAB, PLOT_LINEAR_XLABEL, PLOT_LINEAR_YLABEL, PLOT_SP_LINEAR_POLY_COLOR, PLOT_SP_LINEAR_POLY_LABEL, PLOT_SP_POINT_COLOR, PLOT_SP_POINT_LABEL, PLOT_SP_POLY_COLOR, PLOT_SP_POLY_LABEL, PLOT_SP_TITLE_TAB, PLOT_SP_XLABEL, PLOT_SP_YLABEL, PLOT_WIDGET_DPI, PLOT_WIDGET_HEIGHT, PLOT_WIDGET_WIDTH


class FixedPlot(QWidget):

    def __init__(self, title,  parent=None):

        super().__init__(parent)

        # Objects
        self.title = title

        # Widgets
        self.fig = Figure(figsize=(PLOT_WIDGET_WIDTH/PLOT_WIDGET_DPI, PLOT_WIDGET_HEIGHT/PLOT_WIDGET_DPI), dpi=PLOT_WIDGET_DPI)
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


class LinearRegionPlot(FixedPlot):

    def __init__(self, parent=None):
        
        super().__init__(PLOT_LINEAR_TITLE_TAB, parent)

        self.axs.set_xlabel(PLOT_LINEAR_XLABEL)
        self.axs.set_ylabel(PLOT_LINEAR_YLABEL)
        self.axs.grid()


    def plot(self, process_controls):
        
        der_coef = process_controls['10th_der']
        h = process_controls['h']
        H = process_controls['H']
        linear_region = process_controls['linear_region']
        l_h =  list(linear_region.keys())
        
        # Derivative show values
        h_min = math.floor(min(h))
        h_max = math.ceil(max(h))
        samples = len(h)
        h_values = np.linspace(h_min, h_max, samples)
        
        der_values = np.polyval(der_coef, h_values)

        # Plot derivative
        self.axs.plot(h_values, der_values, label=PLOT_LINEAR_DER_LABEL)
        # Plot linear region area
        self.axs.axvspan(l_h[0], l_h[-1], color='r', alpha=0.3, label=PLOT_LINEAR_REGION_LABEL)
        
        self.axs.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=4)
        self.pltCanvas.draw()

class SmokePointPlot(FixedPlot):
    
    def __init__(self, parent=None):

        super().__init__(PLOT_SP_TITLE_TAB, parent)
        self.axs.set_xlabel(PLOT_SP_XLABEL)
        self.axs.set_ylabel(PLOT_SP_YLABEL)
        self.axs.grid()

    def plot(self, process_controls):

        # Raw data
        h_min = min(process_controls['h'])
        h_max = max(process_controls['h'])
        samples = len(process_controls['h'])
        h_points = np.linspace(h_min, h_max, samples)
        sp_h, sp_H = process_controls['sp']

        # Plot fitted poly for H(h)
        tenth_poly = process_controls['10th_poly']
        tenth_poly_values = np.polyval(tenth_poly, h_points)

        # Plot linear poly
        linear_poly = process_controls['linear_poly']
        linear_poly_values = np.polyval(linear_poly, h_points)

        self.axs.plot(h_points, tenth_poly_values, color=PLOT_SP_POLY_COLOR, label=PLOT_SP_POLY_LABEL)
        self.axs.plot(h_points, linear_poly_values, color=PLOT_SP_LINEAR_POLY_COLOR, label=PLOT_SP_LINEAR_POLY_LABEL)
        # Plot sp
        self.axs.axhline(y=sp_H, color='k', linestyle='dashed')
        self.axs.axvline(x=sp_h, color='k', linestyle='dashed')
        self.axs.scatter(sp_h, sp_H, s=50, color=PLOT_SP_POINT_COLOR, label=PLOT_SP_POINT_LABEL.format(sp_h))
        self.axs.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=4)

        self.pltCanvas.draw()

class PolyHeightPlot(FixedPlot):

    def __init__(self, parent=None):

        super().__init__(PLOT_HEIGHT_POLY_TITLE_TAB, parent)
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

