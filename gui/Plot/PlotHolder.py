from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout,QTabWidget, QLabel
import matplotlib.pyplot as plt
import os
import sys


class PlotHolder(QWidget):

    def __init__(self, widgets, parent=None):
        super().__init__(parent)

        # Objects

        # Widgets
        self.tabWidget = QTabWidget(self)        

        # Init routines
        self.setFixedHeight(480)
        self.setFixedWidth(640)

        # -> Assign each widget 
        for widget in widgets:
            self.tabWidget.addTab(widget, widget.getTitle())

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)

    def addTab(self, widget):
        self.tabWidget.addTab(widget, widget.getTitle())


    def setCurrentTab(self, index):
        self.tabWidget.setCurrentIndex(index)


if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    widget = PlotHolder()
    widget.show()
    sys.exit(app.exec_())
