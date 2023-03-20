from PySide2.QtWidgets import QPushButton, QWidget, QHBoxLayout
from PySide2.QtCore import Signal

class LowerButtons(QWidget):
    apply = Signal()
    save = Signal()
    load = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Objects

        # Widgets
        self.apply_button = QPushButton('Apply')
        self.save_button = QPushButton('Save')
        self.load_button = QPushButton('Load')

        # init routines

        # Signals and Slots
        self.apply_button.clicked.connect(lambda: self.apply.emit())
        self.save_button.clicked.connect(lambda: self.save.emit())
        self.load_button.clicked.connect(lambda: self.load.emit())

        # Layout

        layout = QHBoxLayout()

        layout.addWidget(self.apply_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.load_button)

        self.setLayout(layout)