import datetime
import json
import time

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from apis.realtime_price import fetch_sina_realtime_price
from conf.conf import strategies_config_path
from strategies.common import get_latest_batch_data, calc_wpct


class TurtleInfo:
    def __init__(self):
        self.name = '海龟交易法'
        self.desc = '''
        唐奇安通道
        上轨 = 前20(m)日最高价的最大值
        下轨 = 前10(n)日最低价的最小值
        突破上轨，即认为上涨趋势，做多。突破下轨即认为下跌趋势，做空。
        选股时，还有3(k)个点即将突破上轨，或者刚突破3(k)个点以内，即被选中。
        '''
        self.choose_flag = True
        self.watch_flag = True


class Turtle:
    def __init__(self):
        self.config_path = strategies_config_path.joinpath('turtle.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
        else:
            self.m = 20
            self.n = 10
            self.k = 3

    def calc_batch_up(self, highs):
        ups = []
        for i in range(len(highs)):
            if i < self.m - 1:
                continue
            up = max(highs[i - self.m + 1: i + 1])
            ups.append(up)
        _ups = [0] * self.m
        ups = _ups + ups
        return ups

    def calc_batch_down(self, lows):
        downs = []
        for i in range(len(lows)):
            if i < self.n - 1:
                continue
            down = min(lows[i - self.n + 1: i + 1])
            downs.append(down)
        _downs = [0] * self.n
        downs = _downs + downs
        return downs

    def backtest(self, code, s_date, e_date, init_money, fee, pass_fee, tax):
        dates, opens, closes, highs, lows, volumes, amount, turn, pct_chg, \
        ma_price, mv_volume = get_latest_batch_data(code, s_date=s_date,
                                                    e_date=e_date)
        ups = self.calc_batch_up(highs)
        downs = self.calc_batch_down(lows)
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
        for i in range(len(closes)):
            if i < start:
                continue
            if highs[i] >= ups[i]:
                state = 'b'
                if state != old_state:
                    buy_prices.append(closes[i])
                    buy_dates.append(dates[i])
                    buy_index.append(i)
                    old_state = state
            elif lows[i] < downs[i]:
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
        up = self.calc_batch_up(highs)[-1]
        price = closes[-1]
        if round((abs(up - price) / price), 3) * 100 <= self.k:
            return True
        else:
            return False


class TurtleBacktest(QThread):
    progress_signal = Signal(int, str, str, float, float, float)

    def __init__(self, stocks, s_date, e_date, init_money, fee, pass_fee, tax,
                 parent=None):
        super(TurtleBacktest, self).__init__(parent)
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
        turtle = Turtle()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            wpct, _return, max_drawdown, \
            opens, closes, highs, lows, volumes, dates, \
            opening_index_slices, opening_price_slices, \
            closing_index_slices, closing_price_slices = \
                turtle.backtest(code, self.s_date, self.e_date, self.init_money,
                                self.fee, self.pass_fee, self.tax)
            self.progress_signal.emit(j, code, self.names[i - 1],
                                      wpct, _return, max_drawdown)
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '', 0.0, 0.0, 0.0)


class TurtleChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(TurtleChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

    def run(self):
        turtle = Turtle()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            ret = turtle.choose(code)
            if not ret:
                continue
            self.progress_signal.emit(j, code, self.names[i - 1])
            if i % step == 0:
                j += 1
            # For test, keep it.
            # if j == 1:
            #     self.progress_signal.emit(100, '', '')
            #     return
            # Test end
        self.progress_signal.emit(100, '', '')


class TurtleWatch(QThread):
    up_signal = Signal(str, str, str, float, float)
    down_signal = Signal(str, str, str, float, float)

    def __init__(self, stocks, parent=None):
        super(TurtleWatch, self).__init__(parent)
        self.name = TurtleInfo().name
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

    def _get_up_data(self, code):
        date, _open, close, high, low, volume, amount, turn, pct_chg, \
        ma_price, ma_volume = \
            get_latest_batch_data(code, limit=self.m)
        return high

    def _calc_up(self, code):
        data = self._get_up_data(code)
        up = max(data)
        return up

    def _get_down_data(self, code):
        date, _open, close, high, low, volume, amount, turn, pct_chg, \
        ma_price, ma_volume = \
            get_latest_batch_data(code, limit=self.n)
        return low

    def _calc_down(self, code):
        data = self._get_down_data(code)
        down = min(data)
        return down

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


# TODO: line color
class TurtleConfig(QDialog):
    def __init__(self, parent=None):
        super(TurtleConfig, self).__init__(parent)
        self.setWindowTitle('海龟交易策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = strategies_config_path.joinpath('turtle.json')
        self.info = TurtleInfo()

        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
        else:
            self.m = 20
            self.n = 10
            self.k = 3

        reg = QRegExp('[0-9]+$')
        validator = QRegExpValidator()
        validator.setRegExp(reg)

        main_f_box = QFormLayout()
        self.desc = QTextEdit()
        self.desc.setReadOnly(True)
        self.desc.setText(self.info.desc)
        self.m_label = QLabel('上轨周期m')
        self.m_input = QLineEdit(str(self.m))
        self.m_input.setValidator(validator)
        self.n_label = QLabel('下轨周期n')
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
    main = TurtleConfig()
    main.show()

    sys.exit(app.exec_())
