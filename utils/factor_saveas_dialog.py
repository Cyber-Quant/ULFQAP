from pathlib import Path
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from conf.conf import factor_strategies_config_path


class FactorSaveAsDialog(QDialog):
    factor_saveas_signal = Signal(str)

    def __init__(self, parent=None):
        super(FactorSaveAsDialog, self).__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        self.title = QLabel('因子策略另存为')
        self.name_label = QLabel('新名字')
        self.name_input = QLineEdit()
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_form_box = QFormLayout()
        main_form_box.addRow(self.title)
        main_form_box.addRow(self.name_label, self.name_input)
        main_form_box.addRow(self.btn_cancel, self.btn_ok)
        self.setLayout(main_form_box)

        self.btn_cancel.clicked.connect(self.close)
        self.btn_ok.clicked.connect(self.on_ok)

    def on_ok(self):
        name = self.name_input.text().strip()
        flag = False
        for file in Path(factor_strategies_config_path).rglob('*.json'):
            if name == file.stem:
                flag = True
        if flag:
            QMessageBox.warning(self, '警告', '策略已存在，请换一个名字',
                                QMessageBox.Ok, QMessageBox.Ok)
        else:
            self.factor_saveas_signal.emit(name)
            self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = FactorSaveAsDialog()
    main.show()
    sys.exit(app.exec_())
