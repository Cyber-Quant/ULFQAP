from PySide2 import QtCore
from PySide2.QtWidgets import *

from pages.main_win import MainWin

if __name__ == '__main__':
    import sys

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    main_app = QApplication(sys.argv)
    main_window = MainWin()
    main_window.show()
    sys.exit(main_app.exec_())
