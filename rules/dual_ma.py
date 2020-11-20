import json
import numpy as np

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import rules_config_path, DEFAULT_K_DAYS
from rules.base import get_latest_n_desc_data


class DualMAInfo:
    def __init__(self):
        self.name = '双均线'
        self.desc = '''
        双均线
        短期均线 = 20(m)日的移动平均线(SMA)
        长期均线 = 55(n)日的SMA
        短期均线向上突破长期均线，即认为上涨趋势，做多。向下突破即认为下跌趋势，做空。
        选股时，还有3(k)个点即将突破上轨，或者刚突破3(k)个点以内，即被选中。
        '''
        self.choose_flag = True
        self.watch_flag = False


class DualMAChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(DualMAChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = rules_config_path.joinpath('dual_ma.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
        else:
            self.m = 20
            self.n = 55
            self.k = 3

    def _get_short_period_data(self, code):
        rows = get_latest_n_desc_data(code, self.m)
        data = []
        for row in rows:
            data.append(row.close)
        return data

    def _calc_short_period_ma(self, code):
        data = self._get_short_period_data(code)
        ma = np.mean(data)
        return ma

    def _get_long_period_data(self, code):
        rows = get_latest_n_desc_data(code, self.n)
        data = []
        for row in rows:
            data.append(row.close)
        return data

    def _calc_long_period_ma(self, code):
        data = self._get_long_period_data(code)
        ma = np.mean(data)
        return ma

    def choose(self, code):
        sma = self._calc_short_period_ma(code)
        lma = self._calc_long_period_ma(code)
        if round((abs(sma - lma) / lma), 3) * 100 <= self.k:
            return True
        else:
            return False

    def run(self):
        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            ret = self.choose(code)
            if not ret:
                continue
            self.progress_signal.emit(j, code, self.names[i - 1])
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '')


class DualMA:
    def __init__(self):
        self.config_path = rules_config_path.joinpath('dual_ma.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
        else:
            self.m = 20
            self.n = 55
            self.k = 3

    def _get_batch_close_data(self, code):
        rows = get_latest_n_desc_data(code, DEFAULT_K_DAYS)
        data = []
        for row in rows:
            data.append(row.close)
        return data[::-1]

    def _calc_batch_ma(self, code, period):
        data = self._get_batch_close_data(code)
        mas = []
        for i in range(len(data)):
            if i < period - 1:
                continue
            ma = np.mean(data[i - period + 1: i + 1])
            mas.append(ma)
        return mas

    def calc_short_period_ma(self, code):
        short_period_mas = self._calc_batch_ma(code, self.m)
        _short_period_mas = [0] * self.m
        short_period_mas = _short_period_mas + short_period_mas
        return short_period_mas

    def calc_long_period_ma(self, code):
        long_period_mas = self._calc_batch_ma(code, self.n)
        _long_period_mas = [0] * self.n
        long_period_mas = _long_period_mas + long_period_mas
        return long_period_mas


class DualMAConfig(QDialog):
    def __init__(self, parent=None):
        super(DualMAConfig, self).__init__(parent)
        self.setWindowTitle('双均线策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = rules_config_path.joinpath('dual_ma.json')
        self.info = DualMAInfo()

        reg = QRegExp('[0-9]+$')
        validator = QRegExpValidator()
        validator.setRegExp(reg)

        main_f_box = QFormLayout()
        self.desc = QTextEdit()
        self.desc.setReadOnly(True)
        self.desc.setText(self.info.desc)
        self.m_label = QLabel('短周期m')
        self.m_input = QLineEdit()
        self.m_input.setValidator(validator)
        self.n_label = QLabel('长周期n')
        self.n_input = QLineEdit()
        self.n_input.setValidator(validator)
        self.k_label = QLabel('k个点')
        self.k_input = QLineEdit()
        self.k_input.setValidator(validator)
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_f_box.addRow(self.desc)
        main_f_box.addRow(self.m_label, self.m_input)
        main_f_box.addRow(self.n_label, self.n_input)
        main_f_box.addRow(self.k_label, self.k_input)
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
        data['n'] = int(self.n_input.text())
        data['k'] = int(self.k_input.text())
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = DualMAConfig()
    main.show()

    sys.exit(app.exec_())
