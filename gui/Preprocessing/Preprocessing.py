from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QTabWidget

class PreprocessingWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # Objects


        # Widgets
        self.description = QLabel('probando', self)
        self.tabs = QTabWidget(self)


        # Init routines


        # Signals and Slots


        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.description)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def addTab(self, widget, label):
        self.tabs.addTab(widget, label)