import sys
from Main import HairFollicle_mainpage
from PyQt5.QtWidgets import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = HairFollicle_mainpage()
    win.showMaximized()
    sys.exit(app.exec_())