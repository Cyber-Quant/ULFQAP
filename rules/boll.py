import json
import numpy as np
import time

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from apis.realtime_price import fetch_sina_realtime_price
from conf.conf import rules_config_path, DEFAULT_K_DAYS
from rules.base import get_latest_n_desc_data, get_last_desc_data


class BOLLInfo:
    def __init__(self):
        self.name = '布林带'
        self.desc = '''
        布林带
        中轨线 = 20(m)日的移动平均线(SMA)
        上轨线 = 20(m)日的SMA + 2(k)倍 20(m)日的标准差
        下轨线 = 20(m)日的SMA - 2(k)倍 20(m)日的标准差
        突破上轨，即认为上涨趋势，做多。突破下轨即认为下跌趋势，做空。
        选股时，还有3(n)个点即将突破上轨，或者刚突破3(n)个点以内，即被选中。
        
        5(j)日内，触底反弹
        5(j)日内，向上开口
        '''
        self.choose_flag = True
        self.watch_flag = True


class BOLLChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(BOLLChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = rules_config_path.joinpath('boll.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.k = data['k']
                self.n = data['n']
                self.j = data['j']
                self.break_up = data['break_up']
                self.rebound = data['rebound']
                self.open_up = data['open_up']
        else:
            self.m = 20
            self.k = 2
            self.n = 3
            self.j = 5
            self.break_up = True
            self.rebound = False
            self.open_up = False

    def _get_batch_data(self, code, days):
        rows = get_latest_n_desc_data(code, days + self.m)
        close = []
        high = []
        low = []
        for row in rows:
            close.append(row.close)
            high.append(row.close)
            low.append(row.close)
        return close[::-1], high[::-1], low[::-1]

    def _calc_batch_std(self, data):
        stds = []
        for i in range(len(data)):
            if i < self.m:
                continue
            std = np.std(data[i - self.m + 1:i + 1], ddof=1)
            stds.append(std)
        _stds = [0] * self.m
        stds = _stds + stds
        return stds

    def _calc_batch_middle(self, data):
        middles = []
        for i in range(len(data)):
            if i < self.m:
                continue
            middle = np.mean(data[i - self.m + 1:i + 1])
            middles.append(middle)
        _middles = [0] * self.m
        middles = _middles + middles
        return middles

    def _calc_batch_down(self, data):
        stds = self._calc_batch_std(data)
        middles = self._calc_batch_middle(data)
        downs = []
        for i, middle in enumerate(middles):
            down = middle - self.k * stds[i]
            downs.append(down)
        return downs

    def _calc_batch_up(self, data):
        stds = self._calc_batch_std(data)
        middles = self._calc_batch_middle(data)
        ups = []
        for i, middle in enumerate(middles):
            up = middle + self.k * stds[i]
            ups.append(up)
        return ups

    def choose(self, code):
        closes, highs, lows = self._get_batch_data(code, self.j)
        ups = self._calc_batch_up(closes)
        downs = self._calc_batch_down(closes)
        middles = self._calc_batch_middle(closes)
        last_high_price = highs[-1]
        last_up = ups[-1]

        if self.break_up:
            if round((abs(last_up - last_high_price) / last_high_price),
                     3) * 100 <= self.n:
                return True
        elif self.rebound:
            idx = lows.index(min(lows))
            if idx > 0 and \
                    lows[idx] < downs[idx] and \
                    closes[0] >= downs[0] and \
                    closes[0] > closes[idx]:
                return True
            if idx > 0 and \
                    lows[idx] >= downs[idx] and \
                    round((lows[idx] - downs[idx]) / lows[idx],
                          3) * 100 <= self.n and \
                    closes[0] >= downs[0] and \
                    closes[0] > closes[idx]:
                return True
        elif self.open_up:
            for i in range(self.j):
                if closes[-i - 1] >= middles[-i - 1] and \
                        ups[-i - 1] >= ups[-i - 2]:
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


class BOLLWatch(QThread):
    up_signal = Signal(str, str, str, float, float)
    down_signal = Signal(str, str, str, float, float)

    def __init__(self, stocks, parent=None):
        super(BOLLWatch, self).__init__(parent)
        self.name = BOLLInfo().name
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = rules_config_path.joinpath('boll.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.k = data['k']
                self.n = data['n']
        else:
            self.m = 20
            self.k = 2
            self.n = 3

    def _get_close_data(self, code):
        rows = get_latest_n_desc_data(code, self.m)
        data = []
        for row in rows:
            data.append(row.close)
        return data

    def _calc_std(self, code):
        data = self._get_close_data(code)
        std = np.std(data, ddof=1)
        return std

    def _calc_middle(self, code):
        data = self._get_close_data(code)
        middle = np.mean(data)
        return middle

    def _calc_down(self, code):
        middle = self._calc_middle(code)
        std = self._calc_std(code)
        down = middle - self.k * std
        return down

    def _calc_up(self, code):
        middle = self._calc_middle(code)
        std = self._calc_std(code)
        up = middle + self.k * std
        return up

    def run(self):
        watch_ups = []
        watch_downs = []
        pre_prices = []
        for code in self.codes:
            watch_ups.append(self._calc_up(code))
            watch_downs.append(self._calc_down(code))
            pre_prices.append(0.0)
        while True:
            prices = fetch_sina_realtime_price(self.codes)
            for i, price in enumerate(prices):
                if pre_prices[i] <= watch_ups[i] < price:
                    self.up_signal.emit(self.name,
                                        self.codes[i], self.names[i],
                                        watch_ups[i], price)
                if pre_prices[i] >= watch_downs[i] > price:
                    self.down_signal.emit(self.name,
                                          self.codes[i], self.names[i],
                                          watch_downs[i], price)
                pre_prices[i] = price
            time.sleep(3)


class BOLL:
    def __init__(self):
        self.config_path = rules_config_path.joinpath('boll.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.k = data['k']
                self.n = data['n']
        else:
            self.m = 20
            self.k = 2
            self.n = 3

    def _get_close_data(self, code):
        rows = get_latest_n_desc_data(code, self.m)
        data = []
        for row in rows:
            data.append(row.close)
        return data

    def _calc_std(self, code):
        data = self._get_close_data(code)
        std = np.std(data, ddof=1)
        return std

    def calc_middle(self, code):
        data = self._get_close_data(code)
        middle = np.mean(data)
        return middle

    def calc_down(self, code):
        middle = self.calc_middle(code)
        std = self._calc_std(code)
        down = middle - self.k * std
        return down

    def calc_up(self, code):
        middle = self.calc_middle(code)
        std = self._calc_std(code)
        up = middle + self.k * std
        return up

    def _get_batch_close_data(self, code):
        rows = get_latest_n_desc_data(code, DEFAULT_K_DAYS)
        data = []
        for row in rows:
            data.append(row.close)
        return data[::-1]

    def _calc_batch_std(self, code):
        data = self._get_batch_close_data(code)
        stds = []
        for i in range(len(data)):
            if i < self.m:
                continue
            std = np.std(data[i - self.m + 1:i + 1], ddof=1)
            stds.append(std)
        _stds = [0] * self.m
        stds = _stds + stds
        return stds

    def calc_batch_middle(self, code):
        data = self._get_batch_close_data(code)
        middles = []
        for i in range(len(data)):
            if i < self.m:
                continue
            middle = np.mean(data[i - self.m + 1:i + 1])
            middles.append(middle)
        _middles = [0] * self.m
        middles = _middles + middles
        return middles

    def calc_batch_down(self, code):
        stds = self._calc_batch_std(code)
        middles = self.calc_batch_middle(code)
        downs = []
        for i, middle in enumerate(middles):
            down = middle - self.k * stds[i]
            downs.append(down)
        return downs

    def calc_batch_up(self, code):
        stds = self._calc_batch_std(code)
        middles = self.calc_batch_middle(code)
        ups = []
        for i, middle in enumerate(middles):
            up = middle + self.k * stds[i]
            ups.append(up)
        return ups


class BOLLConfig(QDialog):
    def __init__(self, parent=None):
        super(BOLLConfig, self).__init__(parent)
        self.setWindowTitle('布林带策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = rules_config_path.joinpath('boll.json')
        self.info = BOLLInfo()

        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.k = data['k']
                self.n = data['n']
                self.j = data['j']
                self.break_up = data['break_up']
                self.rebound = data['rebound']
                self.open_up = data['open_up']
        else:
            self.m = 20
            self.k = 2
            self.n = 3
            self.j = 5
            self.break_up = True
            self.rebound = False
            self.open_up = False

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
        self.days_label = QLabel('周期m')
        self.days_input = QLineEdit(str(self.m))
        self.days_input.setValidator(validator)
        self.k_label = QLabel('系数k')
        self.k_input = QLineEdit(str(self.k))
        self.k_input.setValidator(float_validator)
        self.n_label = QLabel('n个点')
        self.n_input = QLineEdit(str(self.n))
        self.n_input.setValidator(validator)
        self.j_label = QLabel('周期j')
        self.j_input = QLineEdit(str(self.j))
        self.j_input.setValidator(validator)
        self.break_up_check = QCheckBox('突破上轨')
        if self.break_up:
            self.break_up_check.setChecked(True)
        else:
            self.break_up_check.setChecked(False)
        self.rebound_check = QCheckBox('触底反弹')
        if self.rebound:
            self.rebound_check.setChecked(True)
        else:
            self.rebound_check.setChecked(False)
        self.open_up_check = QCheckBox('向上开口')
        if self.open_up:
            self.open_up_check.setChecked(True)
        else:
            self.open_up_check.setChecked(False)
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_f_box.addRow(self.desc)
        main_f_box.addRow(self.days_label, self.days_input)
        main_f_box.addRow(self.k_label, self.k_input)
        main_f_box.addRow(self.n_label, self.n_input)
        main_f_box.addRow(self.j_label, self.j_input)
        main_f_box.addRow(self.break_up_check)
        main_f_box.addRow(self.rebound_check)
        main_f_box.addRow(self.open_up_check)
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
        data['m'] = int(self.days_input.text())
        data['k'] = int(self.k_input.text())
        data['n'] = int(self.n_input.text())
        data['j'] = int(self.j_input.text())
        if self.break_up_check.isChecked():
            data['break_up'] = True
        else:
            data['break_up'] = False
        if self.rebound_check.isChecked():
            data['rebound'] = True
        else:
            data['rebound'] = False
        if self.open_up_check.isChecked():
            data['open_up'] = True
        else:
            data['open_up'] = False
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = BOLLConfig()
    main.show()

    sys.exit(app.exec_())
