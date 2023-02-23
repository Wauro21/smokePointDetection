import sys
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QRadioButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
from GUI_CONSTANTS import FrameTypes

class VideoButtons(QWidget):
    frame_selection = pyqtSignal(FrameTypes)
    def __init__(self, parent=None):
        super().__init__(parent)

        # Objects
        self.controls = []

        # Widgets
        self.title = QLabel('Frame Controls:')
        
        self.original = FrameSelector('Default', FrameTypes.FRAME, self)
        self.gray = FrameSelector('Gray', FrameTypes.GRAY, self)
        self.core = FrameSelector('Core', FrameTypes.CORE, self)
        self.contour = FrameSelector('Contour', FrameTypes.CONTOUR, self)
        self.core_mask = FrameSelector('Core Mask', FrameTypes.CORE_CC, self)
        self.contour_mask = FrameSelector('Contour Mask', FrameTypes.CONTOUR_CC, self)

        # Init routines
        self.title.setStyleSheet('font-weight:bold')
        self.original.toggle()
        self.controls = [self.original, self.gray, self.core, self.contour, self.core_mask, self.contour_mask]
        
        # Signals and Slots
        for ctrl in self.controls:
            ctrl.clicked.connect(self.frameSelection)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.title)
        for ctrl in self.controls:
            layout.addWidget(ctrl)

        self.setLayout(layout)

    def frameSelection(self):
        # Search for button checked
        selection = None
        for btn in self.controls:
            if btn.isChecked():
                selection = btn.getFrame()
                break
        self.frame_selection.emit(selection)
        
        

class FrameSelector(QRadioButton):

    def __init__(self, text, frame_value, parent=None):
        super().__init__(text, parent)
        self.frame_sel = frame_value

    def getFrame(self):
        return self.frame_sel




if __name__ == '__main__':
    app = QApplication([])
    test = VideoButtons()
    test.show()
    sys.exit(app.exec_())