from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from conf.conf import licence_html_path


def get_html():
    with open(licence_html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return html


class License(QDialog):
    def __init__(self, parent=None):
        super(License, self).__init__(parent)
        self.setWindowTitle('用户协议')
        self.resize(800, 600)
        self.setWindowModality(Qt.WindowModal)

        main_v_box = QVBoxLayout()
        self.warning_text = QTextEdit()
        self.warning_text.setReadOnly(True)
        self.warning_text.setHtml(get_html())

        op_h_box = QHBoxLayout()
        self.btn_ok = QPushButton('确定')
        op_h_box.addStretch()
        op_h_box.addWidget(self.btn_ok)

        main_v_box.addWidget(self.warning_text)
        main_v_box.addLayout(op_h_box)
        self.setLayout(main_v_box)

        self.btn_ok.clicked.connect(self.close)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = License()
    w.show()
    sys.exit(app.exec_())
