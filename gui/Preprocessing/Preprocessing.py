from PySide2.QtWidgets import QWidget, QVBoxLayout, QTabWidget

class PreprocessingWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # Objects


        # Widgets
        self.tabs = QTabWidget(self)


        # Init routines

        # Signals and Slots

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def requestClose(self):
        self.close()

    def addTab(self, widget, enabled):
        index = self.tabs.addTab(widget, widget.getTitle())
        self.tabs.setTabEnabled(index, enabled)
        return index

    def setTabEnabled(self, index, value):
        self.tabs.setTabEnabled(index, value)

    def setCurrentIndex(self, index):
        self.tabs.setCurrentIndex(index)