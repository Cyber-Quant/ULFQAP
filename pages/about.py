from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from conf.version import RELEASE, name, channel, major, minor, fix
from pages.license import License


class About(QDialog):
    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.setWindowTitle('关于')
        self.setWindowModality(Qt.WindowModal)

        main_v_box = QVBoxLayout()
        if channel == RELEASE:
            ver_info = 'v' + str(major) + '.' + str(minor) + '.' + str(
                fix)
        else:
            ver_info = 'v' + str(major) + '.' + str(minor) + '.' + str(
                fix) + '(' + channel + ')'
        self.name_label = QLabel(name)
        self.version_label = QLabel(ver_info)
        self.btn_license = QPushButton('查看用户协议')
        self.btn_license.setFlat(True)
        self.btn_license.setStyleSheet(
            'QPushButton {background-color: #A3C1DA; color: red;}')

        op_h_box = QHBoxLayout()
        self.btn_ok = QPushButton('确定')
        op_h_box.addStretch()
        op_h_box.addWidget(self.btn_ok)

        main_v_box.addWidget(self.name_label)
        main_v_box.addWidget(self.version_label)
        main_v_box.addWidget(self.btn_license)
        main_v_box.addLayout(op_h_box)
        self.setLayout(main_v_box)

        self.btn_ok.clicked.connect(self.close)
        self.btn_license.clicked.connect(self.on_show_license)

    def on_show_license(self):
        dlg = License(self)
        dlg.show()
        dlg.exec_()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = About()
    w.show()
    sys.exit(app.exec_())
