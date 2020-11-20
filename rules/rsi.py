import json

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import rules_config_path, DEFAULT_K_DAYS
from rules.base import get_latest_n_desc_data


class RSIInfo:
    def __init__(self):
        self.name = 'RSI指数'
        self.desc = '''
        RSI指数
        6(m)日RSI = 6(m)日内收盘涨幅的平均值/(6(m)日内收盘涨幅均值+6(m)日内收盘跌幅均值) ×100
        6(m)日RSI和12(n)日RSI均小于50，6(m)日RSI上穿12(n)日RSI，做多。
        6(m)日RSI和12(n)日RSI均大于50，6(m)日RSI下穿12(n)日RSI，做空。
        '''
        self.choose_flag = True
        self.watch_flag = False


class RSIChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(RSIChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = rules_config_path.joinpath('rsi.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
        else:
            self.m = 6
            self.n = 12

    def _get_batch_close_data(self, code):
        rows = get_latest_n_desc_data(code, DEFAULT_K_DAYS)
        closes = []
        for row in rows:
            closes.append(row.close)
        return closes[::-1]

    def _calc_rsi(self, code, period):
        data = self._get_batch_close_data(code)
        length = len(data)
        rsi = [0] * length
        if length <= period:
            return rsi

        up_avg = 0
        down_avg = 0
        first_slice = data[:period + 1]
        for i in range(1, len(first_slice)):
            if first_slice[i] >= first_slice[i - 1]:
                up_avg += first_slice[i] - first_slice[i - 1]
            else:
                down_avg += first_slice[i - 1] - first_slice[i]
        up_avg = up_avg / period
        # When the stock is suspend, the ohlc keep the same value
        # Save the same prices
        if down_avg == 0:
            down_avg = 0.01
        down_avg = down_avg / period
        rs = up_avg / down_avg
        rsi[period] = 100 - 100 / (1 + rs)

        for j in range(period + 1, length):
            if data[j] >= data[j - 1]:
                up = data[j] - data[j - 1]
                down = 0
            else:
                up = 0
                down = data[j - 1] - data[j]

            up_avg = (up_avg * (period - 1) + up) / period
            down_avg = (down_avg * (period - 1) + down) / period
            rs = up_avg / down_avg
            rsi[j] = 100 - 100 / (1 + rs)
        return rsi

    def choose(self, code):
        fast_rsi = self._calc_rsi(code, self.m)
        slow_rsi = self._calc_rsi(code, self.n)
        if (slow_rsi[-1] < 50 and fast_rsi[-1] < 50) and \
                (fast_rsi[-1] >= slow_rsi[-1] and fast_rsi[-2] < slow_rsi[-2]):
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


class RSI:
    def __init__(self):
        self.config_path = rules_config_path.joinpath('rsi.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
        else:
            self.m = 6
            self.n = 12

    def _calc_rsi(self, data, period):
        length = len(data)
        rsi = [0] * length
        if length <= period:
            return rsi

        up_avg = 0
        down_avg = 0
        first_slice = data[:period + 1]
        for i in range(1, len(first_slice)):
            if first_slice[i] >= first_slice[i - 1]:
                up_avg += first_slice[i] - first_slice[i - 1]
            else:
                down_avg += first_slice[i - 1] - first_slice[i]
        up_avg = up_avg / period
        # When the stock is suspend, the ohlc keep the same value
        # Save the same prices
        if down_avg == 0:
            down_avg = 0.01
        down_avg = down_avg / period
        rs = up_avg / down_avg
        rsi[period] = 100 - 100 / (1 + rs)

        for j in range(period + 1, length):
            if data[j] >= data[j - 1]:
                up = data[j] - data[j - 1]
                down = 0
            else:
                up = 0
                down = data[j - 1] - data[j]

            up_avg = (up_avg * (period - 1) + up) / period
            down_avg = (down_avg * (period - 1) + down) / period
            rs = up_avg / down_avg
            rsi[j] = 100 - 100 / (1 + rs)
        return rsi

    def calc_rsi(self, closes):
        fast_rsi = self._calc_rsi(closes, self.m)
        slow_rsi = self._calc_rsi(closes, self.n)
        return fast_rsi, slow_rsi


class RSIConfig(QDialog):
    def __init__(self, parent=None):
        super(RSIConfig, self).__init__(parent)
        self.setWindowTitle('RSI策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = rules_config_path.joinpath('rsi.json')
        self.info = RSIInfo()

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
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_f_box.addRow(self.desc)
        main_f_box.addRow(self.m_label, self.m_input)
        main_f_box.addRow(self.n_label, self.n_input)
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
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = RSIConfig()
    main.show()

    sys.exit(app.exec_())
