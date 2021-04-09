import json

from PySide2.QtCore import *
from PySide2.QtWidgets import *

from conf.conf import global_config_path
from pages.license import get_html
from pages.nav import Nav


class MainWin(QWidget):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(800, 600)

        if global_config_path.exists():
            with open(global_config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'agree' in data:
                    agree = data['agree']
                else:
                    agree = False
                if agree:
                    self._on_continue()
                    return

        self.nav = None
        self.setWindowTitle('用户协议')

        main_v_box = QVBoxLayout()

        op_h_box = QHBoxLayout()
        self.btn_continue = QPushButton('接受，继续')
        self.btn_exit = QPushButton('不接受，退出')
        op_h_box.addStretch()
        op_h_box.addWidget(self.btn_exit)
        op_h_box.addWidget(self.btn_continue)
        op_h_box.addStretch()

        content_v_box = QVBoxLayout()
        self.warning_text = QTextEdit()
        self.warning_text.setReadOnly(True)
        self.warning_text.setHtml(get_html())
        self.agree_check = QCheckBox('不再显示')
        content_v_box.addWidget(self.warning_text)
        content_v_box.addWidget(self.agree_check)
        content_v_box.addLayout(op_h_box)

        main_v_box.addLayout(content_v_box)
        self.setLayout(main_v_box)

        self.btn_continue.clicked.connect(self.on_continue)
        self.btn_exit.clicked.connect(self.on_exit)

    def on_continue(self):
        if self.agree_check.isChecked():
            if not global_config_path.exists():
                data = {}
            else:
                with open(global_config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            data['agree'] = True
            with open(global_config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        self._on_continue()

    def _on_continue(self):
        self.hide()
        self.nav = Nav()
        self.nav.show()
        self.deleteLater()

    def on_exit(self):
        self.close()


if __name__ == '__main__':
    import sys

    main_app = QApplication(sys.argv)
    main_window = MainWin()
    main_window.show()
    sys.exit(main_app.exec_())
