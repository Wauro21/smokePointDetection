from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout,QTabWidget
import os
import sys

from gui.GUI_CONSTANTS import TABS_WIDGET_HEIGHT, TABS_WIDGET_WIDTH


class TabHolder(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Objects
        self.show_idx = None
        self.invisible = []

        # Widgets
        self.tabWidget = QTabWidget(self)        

        # Init routines
        self.setFixedHeight(TABS_WIDGET_HEIGHT)
        self.setFixedWidth(TABS_WIDGET_WIDTH)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)

    def addTab(self, widget, visible=True, show_tab = False):
        idx = self.tabWidget.addTab(widget, widget.getTitle())
        self.tabWidget.setTabVisible(idx, visible)

        if not(visible):
            self.invisible.append(idx)

        if(show_tab):
            self.show_idx = idx

        return idx

    def setCurrentTab(self, index):
        self.tabWidget.setCurrentIndex(index)

    def showResultTab(self):
        self.tabWidget.setCurrentIndex(self.show_idx)

    def toggleInvinsibles(self):
        for idx in self.invisible:
            status = self.tabWidget.isTabVisible(idx)
            self.tabWidget.setTabVisible(idx, not status)

    def setInvisibles(self, lock):
        for idx in self.invisible:
            self.tabWidget.setTabVisible(idx, lock)

if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = PlotHolder()
    widget.show()
    sys.exit(app.exec_())
