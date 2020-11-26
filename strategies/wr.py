import json

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import strategies_config_path, DEFAULT_K_LIMIT
from strategies.base import get_latest_n_desc_data


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


# TODO: Separate common code
class WRChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(WRChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = strategies_config_path.joinpath('wr.json')
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
        rows = get_latest_n_desc_data(code, DEFAULT_K_LIMIT)
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


# TODO: Separate common code
class WR:
    def __init__(self):
        self.config_path = strategies_config_path.joinpath('wr.json')
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

    def _get_batch_data(self, code):
        rows = get_latest_n_desc_data(code, DEFAULT_K_LIMIT)
        _open = []
        close = []
        high = []
        low = []
        volume = []
        date = []
        for row in rows:
            _open.append(row.open)
            close.append(row.close)
            high.append(row.high)
            low.append(row.low)
            volume.append(row.volume)
            date.append(row.date)
        return _open[::-1], close[::-1], high[::-1], low[::-1], \
               volume[::-1], date[::-1]

    def backtest(self, code, init_money, fee, pass_fee, tax):
        opens, closes, highs, lows, volumes, dates = \
            self._get_batch_data(code)
        wrs = self.calc_williams(closes, highs, lows)
        start = self.m
        buy_prices = []
        buy_dates = []
        buy_index = []
        sell_prices = []
        sell_dates = []
        sell_index = []
        drawdowns = []
        old_state = 's'
        for i in range(len(closes)):
            if i < start:
                continue
            if wrs[i] > self.n:
                state = 'b'
                if state != old_state:
                    buy_prices.append(closes[i])
                    buy_dates.append(dates[i])
                    buy_index.append(i)
                    old_state = state
            elif wrs[i] < self.k:
                state = 's'
                if state != old_state:
                    sell_prices.append(closes[i])
                    sell_dates.append(dates[i])
                    sell_index.append(i)
                    old_state = state
        if len(sell_prices) < len(buy_prices):
            sell_prices.append(closes[-1])
            sell_dates.append(dates[-1])
            sell_index.append(len(buy_prices))

        money = init_money
        opening_index_slices = []
        opening_price_slices = []
        closing_index_slices = []
        closing_price_slices = []
        for i in range(len(buy_prices)):
            hands = int(money * (1 - fee) / buy_prices[i] / 100)
            left_money = money - hands * buy_prices[i] * 100
            sell_money = hands * sell_prices[i] * (1 - tax - pass_fee) * 100
            money = sell_money + left_money

            old_close = buy_prices[i]
            for close in closes[buy_index[i]:sell_index[i] + 1]:
                if close < old_close:
                    old_close = close
            drawdown = buy_prices[i] - old_close / buy_prices[i] * 100
            drawdowns.append(drawdown)
            if i == 0:
                first_start = 0
            else:
                first_start = sell_index[i - 1]
            closing_index = []
            closing_price = []
            for idx in range(first_start, buy_index[i] + 1):
                closing_index.append(idx)
                closing_price.append(closes[idx])
            closing_index_slices.append(closing_index)
            closing_price_slices.append(closing_price)
            opening_index = []
            opening_price = []
            for idx in range(buy_index[i], sell_index[i] + 1):
                opening_index.append(idx)
                opening_price.append(closes[idx])
            if opening_index:
                opening_index_slices.append(opening_index)
                opening_price_slices.append(opening_price)

        _return = (money - init_money) / init_money * 100
        max_drawdown = max(drawdowns)

        return _return, max_drawdown, \
               opens, closes, highs, lows, volumes, dates, \
               opening_index_slices, opening_price_slices, \
               closing_index_slices, closing_price_slices


# TODO: line color, different usage of this strategy
class WRConfig(QDialog):
    def __init__(self, parent=None):
        super(WRConfig, self).__init__(parent)
        self.setWindowTitle('WR策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = strategies_config_path.joinpath('wr.json')
        self.info = WRInfo()

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

        reg = QRegExp('[0-9]+$')
        validator = QRegExpValidator()
        validator.setRegExp(reg)

        main_f_box = QFormLayout()
        self.desc = QTextEdit()
        self.desc.setReadOnly(True)
        self.desc.setText(self.info.desc)
        self.m_label = QLabel('周期m')
        self.m_input = QLineEdit(str(self.m))
        self.m_input.setValidator(validator)
        self.n_label = QLabel('超卖系数n')
        self.n_input = QLineEdit(str(self.n))
        self.n_input.setValidator(validator)
        self.k_label = QLabel('超买系数k')
        self.k_input = QLineEdit(str(self.k))
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
