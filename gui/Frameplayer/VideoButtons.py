import sys
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QRadioButton, QCheckBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
from GUI_CONSTANTS import VIDEO_BUTTONS_WIDGET_HEIGHT, VIDEO_BUTTONS_WIDGET_WIDTH, FrameTypes

class VideoButtons(QWidget):
    frame_selection = pyqtSignal(FrameTypes)
    frame_controls = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)

        # Objects
        self.controls = []
        self.extra_controls = []

        # Widgets
    
        # -> Frame controls
        self.title = QLabel('Frame Controls:')
        self.original = FrameSelector('Default', FrameTypes.FRAME, self)
        self.gray = FrameSelector('Gray', FrameTypes.GRAY, self)
        self.core = FrameSelector('Core', FrameTypes.CORE, self)
        self.contour = FrameSelector('Contour', FrameTypes.CONTOUR, self)
        self.core_mask = FrameSelector('Core Mask', FrameTypes.CORE_CC, self)
        self.contour_mask = FrameSelector('Contour Mask', FrameTypes.CONTOUR_CC, self)

        # -> Extra controls
        self.title_extra = QLabel('Show:')
        self.bbox = QCheckBox('Bounding Boxes')
        self.centroids = QCheckBox('Centroids')
        self.extra_controls = [self.bbox, self.centroids]
        

        # Init routines
        self.setFixedWidth(VIDEO_BUTTONS_WIDGET_WIDTH)
        self.title.setStyleSheet('font-weight:bold')
        self.title_extra.setStyleSheet('font-weight:bold')
        self.original.toggle()
        self.controls = [self.original, self.gray, self.core, self.contour, self.core_mask, self.contour_mask]
        
        # Signals and Slots
        # -> Frame controls
        for ctrl in self.controls:
            ctrl.clicked.connect(self.frameSelection)

        # -> Extra controls
        for extra in self.extra_controls:
            extra.clicked.connect(self.ControlsExtra)

        # Layout
        layout = QVBoxLayout()
        
        # -> Layout for frame controls
        layout.addWidget(self.title)        
        for ctrl in self.controls:
            layout.addWidget(ctrl)

        # -> Layout for extra controls
        extra_options = QVBoxLayout()
        extra_options.addWidget(self.title_extra)
        extra_options.addWidget(self.bbox)
        extra_options.addWidget(self.centroids)
        layout.addLayout(extra_options)

        layout.addStretch()
        self.setLayout(layout)

    def ControlsExtra(self):
        ret_dict = {
            'bboxes': self.bbox.isChecked(),
            'centroids': self.centroids.isChecked()
        }

        self.frame_controls.emit(ret_dict)

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
