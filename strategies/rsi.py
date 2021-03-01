import datetime
import json

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import strategies_config_path
from strategies.common import get_latest_batch_data, calc_wpct


class RSIInfo:
    def __init__(self):
        self.name = 'RSI'
        self.desc = '''
        RSI指数
        6(m)日RSI = 6(m)日内收盘涨幅的平均值/(6(m)日内收盘涨幅均值+6(m)日内收盘跌幅均值) ×100
        6(m)日RSI和12(n)日RSI均小于50，6(m)日RSI上穿12(n)日RSI，做多。
        6(m)日RSI和12(n)日RSI均大于50，6(m)日RSI下穿12(n)日RSI，做空。
        '''
        self.choose_flag = True
        self.watch_flag = False


class RSI:
    def __init__(self):
        self.config_path = strategies_config_path.joinpath('rsi.json')
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

    def backtest(self, code, s_date, e_date, init_money, fee, pass_fee, tax):
        dates, opens, closes, highs, lows, volumes, amount, turn, pct_chg, \
        ma_price, ma_volume = get_latest_batch_data(code, s_date=s_date,
                                                    e_date=e_date)
        fast_rsi = self._calc_rsi(closes, self.m)
        slow_rsi = self._calc_rsi(closes, self.n)
        if self.m > self.n:
            start = self.m
        else:
            start = self.n
        buy_prices = []
        buy_dates = []
        buy_index = []
        sell_prices = []
        sell_dates = []
        sell_index = []
        drawdowns = []
        old_state = 's'
        for i, x in enumerate(closes):
            if i < start:
                continue
            if i == start:
                continue
            if fast_rsi[i] < 50 and slow_rsi[i] < 50 and \
                    fast_rsi[i - 1] < slow_rsi[i - 1] and \
                    fast_rsi[i] >= slow_rsi[i]:
                state = 'b'
                if state != old_state:
                    buy_prices.append(closes[i])
                    buy_dates.append(dates[i])
                    buy_index.append(i)
                    old_state = state
            elif fast_rsi[i] > 50 and slow_rsi[i] > 50 and \
                    fast_rsi[i - 1] >= slow_rsi[i - 1] and \
                    fast_rsi[i] < slow_rsi[i]:
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

        wpct = calc_wpct(buy_prices, sell_prices)
        _return = (money - init_money) / init_money * 100
        max_drawdown = max(drawdowns)

        return wpct, _return, max_drawdown, \
               opens, closes, highs, lows, volumes, dates, \
               opening_index_slices, opening_price_slices, \
               closing_index_slices, closing_price_slices

    def choose(self, code):
        dates, opens, closes, highs, lows, volumes, amount, turn, pct_chg, \
        ma_price, ma_volume = get_latest_batch_data(code)
        fast_rsi = self._calc_rsi(closes, self.m)
        slow_rsi = self._calc_rsi(closes, self.n)
        if (slow_rsi[-1] < 50 and fast_rsi[-1] < 50) and \
                (fast_rsi[-1] >= slow_rsi[-1] and fast_rsi[-2] < slow_rsi[-2]):
            return True
        else:
            return False


class RSIBacktest(QThread):
    progress_signal = Signal(int, str, str, float, float, float)

    def __init__(self, stocks, s_date, e_date, init_money, fee, pass_fee, tax,
                 parent=None):
        super(RSIBacktest, self).__init__(parent)
        self.codes = []
        self.names = []
        self.s_date = datetime.datetime.strptime(s_date, '%Y-%m-%d')
        self.e_date = datetime.datetime.strptime(e_date, '%Y-%m-%d')
        self.init_money = init_money
        self.fee = fee
        self.pass_fee = pass_fee
        self.tax = tax
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

    def run(self):
        rsi = RSI()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            wpct, _return, max_drawdown, \
            opens, closes, highs, lows, volumes, dates, \
            opening_index_slices, opening_price_slices, \
            closing_index_slices, closing_price_slices = \
                rsi.backtest(code, self.s_date, self.e_date, self.init_money,
                             self.fee, self.pass_fee, self.tax)
            self.progress_signal.emit(j, code, self.names[i - 1],
                                      wpct, _return, max_drawdown)
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '', 0.0, 0.0, 0.0)


class RSIChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(RSIChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

    def run(self):
        rsi = RSI()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            ret = rsi.choose(code)
            if not ret:
                continue
            self.progress_signal.emit(j, code, self.names[i - 1])
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '')


# TODO: line color, different usage of this strategy
class RSIConfig(QDialog):
    def __init__(self, parent=None):
        super(RSIConfig, self).__init__(parent)
        self.setWindowTitle('RSI策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = strategies_config_path.joinpath('rsi.json')
        self.info = RSIInfo()

        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
        else:
            self.m = 6
            self.n = 12

        reg = QRegExp('[0-9]+$')
        validator = QRegExpValidator()
        validator.setRegExp(reg)

        main_f_box = QFormLayout()
        self.desc = QTextEdit()
        self.desc.setReadOnly(True)
        self.desc.setText(self.info.desc)
        self.m_label = QLabel('短周期m')
        self.m_input = QLineEdit(str(self.m))
        self.m_input.setValidator(validator)
        self.n_label = QLabel('长周期n')
        self.n_input = QLineEdit(str(self.n))
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
