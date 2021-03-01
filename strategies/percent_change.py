import json
import numpy as np

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import strategies_config_path
from strategies.common import get_latest_batch_data


class PercentChangeInfo:
    def __init__(self):
        self.name = '涨跌幅'
        self.desc = '''
        涨跌幅
        涨跌幅不超过5(m)个点。
        '''
        self.choose_flag = True
        self.watch_flag = False


class PercentChange:
    def __init__(self):
        self.config_path = strategies_config_path.joinpath(
            'percent_change.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
        else:
            self.m = 5

    def _get_percent_change(self, code):
        date, _open, close, high, low, volume, amount, turn, pct_chg, \
        ma_price, ma_volume = \
            get_latest_batch_data(code, self.m)
        return pct_chg

    def choose(self, code):
        pct_chg = self._get_percent_change(code)
        _pct_chg = pct_chg[-1] * 100
        if _pct_chg > self.m:
            return False
        else:
            return True


class PercentChangeChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(PercentChangeChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

    def run(self):
        percent_change = PercentChange()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            ret = percent_change.choose(code)
            if not ret:
                continue
            self.progress_signal.emit(j, code, self.names[i - 1])
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '')


class PercentChangeConfig(QDialog):
    def __init__(self, parent=None):
        super(PercentChangeConfig, self).__init__(parent)
        self.setWindowTitle('涨跌幅策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = strategies_config_path.joinpath(
            'percent_change.json')
        self.info = PercentChangeInfo()

        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
        else:
            self.m = 5

        reg = QRegExp('[0-9]+$')
        validator = QRegExpValidator()
        validator.setRegExp(reg)

        reg = QRegExp('[0-9.]+$')
        float_validator = QRegExpValidator()
        float_validator.setRegExp(reg)

        main_f_box = QFormLayout()
        self.desc = QTextEdit()
        self.desc.setReadOnly(True)
        self.desc.setText(self.info.desc)
        self.m_label = QLabel('m')
        self.m_input = QLineEdit(str(self.m))
        self.m_input.setValidator(validator)
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_f_box.addRow(self.desc)
        main_f_box.addRow(self.m_label, self.m_input)
        main_f_box.addRow(self.btn_cancel, self.btn_ok)
        self.setLayout(main_f_box)

        self.btn_cancel.clicked.connect(self.close)
        self.btn_ok.clicked.connect(self.ok)

    def ok(self):
        if not self.config_path.exists():
            data = {}
        else:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        data['m'] = int(self.m_input.text())
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = PercentChangeConfig()
    main.show()

    sys.exit(app.exec_())
