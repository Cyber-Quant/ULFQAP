import json
import numpy as np

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import strategies_config_path, DEFAULT_K_LIMIT
from strategies.base import get_latest_n_desc_data


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


# TODO: Separate common code
# TODO: Use numpy to speedup
class DualMAChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(DualMAChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = strategies_config_path.joinpath('dual_ma.json')
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


# TODO: Separate common code
# TODO: Use numpy to speedup
class DualMA:
    def __init__(self):
        self.config_path = strategies_config_path.joinpath('dual_ma.json')
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
        rows = get_latest_n_desc_data(code, DEFAULT_K_LIMIT)
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
        slow_mas = self.calc_long_period_ma(code)
        fast_mas = self.calc_short_period_ma(code)
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
            if fast_mas[i] >= slow_mas[i] and fast_mas[i - 1] < slow_mas[i - 1]:
                state = 'b'
                if state != old_state:
                    buy_prices.append(closes[i])
                    buy_dates.append(dates[i])
                    buy_index.append(i)
                    old_state = state
            elif fast_mas[i] < slow_mas[i] and \
                    fast_mas[i - 1] <= slow_mas[i - 1]:
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
class DualMAConfig(QDialog):
    def __init__(self, parent=None):
        super(DualMAConfig, self).__init__(parent)
        self.setWindowTitle('双均线策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = strategies_config_path.joinpath('dual_ma.json')
        self.info = DualMAInfo()

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
        self.k_label = QLabel('k个点')
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
    main = DualMAConfig()
    main.show()

    sys.exit(app.exec_())
