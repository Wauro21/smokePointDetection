
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from gui.GUI_CONSTANTS import PLOT_CENTROID_INVALID_COLOR, PLOT_CENTROID_INVALID_MARKER, PLOT_CENTROID_REFERENCE_COLOR, PLOT_CENTROID_REFERENCE_LINE, PLOT_CENTROID_SAFE_AREA_ALPHA, PLOT_CENTROID_SAFE_AREA_COLOR, PLOT_CENTROID_SAFE_AREA_LIMITS_COLOR, PLOT_CENTROID_SAFE_AREA_LIMITS_LINE, PLOT_CENTROID_TAB_TITLE, PLOT_CENTROID_VALID_COLOR, PLOT_CENTROID_VALID_MARKER, PLOT_CENTROID_XLABEL, PLOT_CENTROID_YLABEL, PLOT_WIDGET_HEIGHT, PLOT_WIDGET_WIDTH, CentroidTypes


class CentroidPlotWidget(QWidget):

    def __init__(self, process_controls, parent=None):

        super().__init__(parent)

        # Objects
        self.process_controls = process_controls
        self.centroid_data = None
        self.title = PLOT_CENTROID_TAB_TITLE
        self.x_axis = PLOT_CENTROID_XLABEL
        self.y_axis = PLOT_CENTROID_YLABEL

        # Widgets
        self.fig = Figure()
        self.pltCanvas = FigureCanvas(self.fig)
        self.pltToolbar = NavigationToolbar(self.pltCanvas)

        # init routines
        self.resetData()
        self.setFixedHeight(PLOT_WIDGET_HEIGHT)
        self.setFixedWidth(PLOT_WIDGET_WIDTH)
        self.axs = self.pltCanvas.figure.gca()
        self.animation = FuncAnimation(self.pltCanvas.figure, self.updatePlot)
        self.animation.pause()

        
        # Signals and Slots

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.pltToolbar)
        layout.addWidget(self.pltCanvas)
        self.setLayout(layout)

    def clearPlot(self):
        self.resetData()
        self.restoreAx()

    def restoreAx(self):
        self.axs.cla()
        self.axs.grid()
        #self.axs.set_title(self.title)
        self.axs.set_xlabel(self.x_axis)
        self.axs.set_ylabel(self.y_axis)


    def updatePlot(self, i):
        self.restoreAx()

        # Plot reference line
        ref_centroid = self.centroid_data[CentroidTypes.REFERENCE]['ref']
        self.axs.axhline(y=ref_centroid, color=PLOT_CENTROID_REFERENCE_COLOR, linestyle=PLOT_CENTROID_REFERENCE_LINE, label='Reference')

        # -> Plot the tolerance area
        tolerance = self.process_controls['controls']['centroid_tol']
        upper = ref_centroid + tolerance
        lower = ref_centroid - tolerance
        self.axs.axhline(y=upper, color=PLOT_CENTROID_SAFE_AREA_LIMITS_COLOR, linestyle=PLOT_CENTROID_SAFE_AREA_LIMITS_LINE)
        self.axs.axhline(y=lower, color=PLOT_CENTROID_SAFE_AREA_LIMITS_COLOR, linestyle=PLOT_CENTROID_SAFE_AREA_LIMITS_LINE)

        # -> Draw the area in between
        self.axs.axhspan(lower, upper, color=PLOT_CENTROID_SAFE_AREA_COLOR, alpha=PLOT_CENTROID_SAFE_AREA_ALPHA, label='Safe area')
        
        # Draw valid centroids 
        valid_frames = self.centroid_data[CentroidTypes.VALID]['frames']
        valid_centroids = self.centroid_data[CentroidTypes.VALID]['centroids']
        self.axs.scatter(valid_frames, valid_centroids, color=PLOT_CENTROID_VALID_COLOR, marker=PLOT_CENTROID_VALID_MARKER, label='Valid')

        # Draw invalid centroids
        invalid_frames = self.centroid_data[CentroidTypes.INVALID]['frames']
        invalid_centroids = self.centroid_data[CentroidTypes.INVALID]['centroids']
        self.axs.scatter(invalid_frames, invalid_centroids, color=PLOT_CENTROID_INVALID_COLOR, marker=PLOT_CENTROID_INVALID_MARKER, label='Invalid')

        self.axs.legend(bbox_to_anchor=(0, 1.02, 1,0.2), loc='lower left', ncol=4)


    def getTitle(self):
        return self.title

    def update(self, message):
        # Classify the message
        message_type = list(message.keys())[-1]
        
        if(message_type == CentroidTypes.REFERENCE):
            ref_value = message[message_type]
            self.centroid_data[message_type]['ref'] = ref_value

        else:
            n_frame = message[message_type][0]
            n_centroid = message[message_type][1]

            # Add the new data
            self.centroid_data[message_type]['frames'].append(n_frame)
            self.centroid_data[message_type]['centroids'].append(n_centroid)



    def resetData(self):
        self.centroid_data = {
            CentroidTypes.REFERENCE: {
                'ref': 0,
            },

            CentroidTypes.VALID: {
                'frames': [],
                'centroids': [],
            },

            CentroidTypes.INVALID: {
                'frames': [],
                'centroids': [],
            },
        }