from qtpy.QtCore import *
from qtpy.QtWidgets import *


class CustomAddDialog(QDialog):
    add_custom_stock_signal = Signal(str, str)

    def __init__(self, parent=None):
        super(CustomAddDialog, self).__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        self.title = QLabel('下拉搜索框下个版本再做，先凑合用')
        self.label = QLabel('一定要写对，错了后面代码都会出错')
        self.code_label = QLabel('代码')
        self.code_input = QLineEdit()
        self.name_label = QLabel('名字')
        self.name_input = QLineEdit()
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_form_box = QFormLayout()
        main_form_box.addRow(self.title)
        main_form_box.addRow(self.label)
        main_form_box.addRow(self.code_label, self.code_input)
        main_form_box.addRow(self.name_label, self.name_input)
        main_form_box.addRow(self.btn_cancel, self.btn_ok)
        self.setLayout(main_form_box)

        self.btn_cancel.clicked.connect(self.close)
        self.btn_ok.clicked.connect(self.on_ok)

    def on_ok(self):
        code = self.code_input.text()
        name = self.name_input.text()
        self.add_custom_stock_signal.emit(code, name)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = CustomAddDialog()
    main.show()
    sys.exit(app.exec_())