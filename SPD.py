# Main handler for GUI/terminal calls
import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.MainWindow import SPDMain







if __name__ == '__main__':
    app = QApplication([])
    if os.name == 'nt':
        app.setStyle('Fusion')
    window = SPDMain()
    window.show()
    # For the moment fix the size
    h = window.height()
    w = window.width()
    window.setFixedSize(w, h)
    sys.exit(app.exec())