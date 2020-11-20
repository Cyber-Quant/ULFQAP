import json

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import rules_config_path, DEFAULT_K_DAYS
from rules.base import get_latest_n_desc_data


class WRInfo:
    def __init__(self):
        self.name = '威廉指数'
        self.desc = '''
        威廉指数
        (30(m)日最高价 - 第30(m)日收盘价) / (30(m)日最高价 - 30(m)日最低价) * 100
        威廉指数大于85(n)，超卖状态，行情即将见底。
        威廉指数小于15(k)，超买状态，行情即将见顶。
        '''
        self.choose_flag = True
        self.watch_flag = False


class WRChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(WRChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = rules_config_path.joinpath('wr.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
        else:
            self.m = 30
            self.n = 85
            self.k = 15

    def _get_batch_data(self, code):
        rows = get_latest_n_desc_data(code, DEFAULT_K_DAYS)
        closes = []
        highs = []
        lows = []
        for row in rows:
            closes.append(row.close)
            highs.append(row.high)
            lows.append(row.low)
        return closes[::-1], highs[::-1], lows[::-1]

    def _calc_williams(self, code):
        closes, highs, lows = self._get_batch_data(code)
        williams = []
        for i, data in enumerate(closes):
            if i < self.m:
                continue
            high_slice = highs[i - self.m + 1:i + 1]
            low_slice = lows[i - self.m + 1:i + 1]
            a = max(high_slice) - closes[i]
            b = max(high_slice) - min(low_slice)
            # When the stock is suspend, the ohlc keep the same value
            # Save the same prices
            if b == 0:
                b = 0.01
            williams.append(a / b * 100)
        _williams = [0] * self.m
        williams = _williams + williams
        return williams

    def choose(self, code):
        williams = self._calc_williams(code)
        if williams[-1] > self.n:
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


class WR:
    def __init__(self):
        self.config_path = rules_config_path.joinpath('wr.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
        else:
            self.m = 30
            self.n = 85
            self.k = 15

    def calc_williams(self, closes, highs, lows):
        williams = []
        for i, data in enumerate(closes):
            if i < self.m:
                continue
            high_slice = highs[i - self.m + 1:i + 1]
            low_slice = lows[i - self.m + 1:i + 1]
            a = max(high_slice) - closes[i]
            b = max(high_slice) - min(low_slice)
            # When the stock is suspend, the ohlc keep the same value
            # Save the same prices
            if b == 0:
                b = 0.01
            williams.append(a / b * 100)
        _williams = [0] * self.m
        williams = _williams + williams
        return williams


class WRConfig(QDialog):
    def __init__(self, parent=None):
        super(WRConfig, self).__init__(parent)
        self.setWindowTitle('WR策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = rules_config_path.joinpath('wr.json')
        self.info = WRInfo()

        reg = QRegExp('[0-9]+$')
        validator = QRegExpValidator()
        validator.setRegExp(reg)

        main_f_box = QFormLayout()
        self.desc = QTextEdit()
        self.desc.setReadOnly(True)
        self.desc.setText(self.info.desc)
        self.m_label = QLabel('周期m')
        self.m_input = QLineEdit()
        self.m_input.setValidator(validator)
        self.n_label = QLabel('超卖系数n')
        self.n_input = QLineEdit()
        self.n_input.setValidator(validator)
        self.k_label = QLabel('超买系数k')
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
    main = WRConfig()
    main.show()

    sys.exit(app.exec_())
