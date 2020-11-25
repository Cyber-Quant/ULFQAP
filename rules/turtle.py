import json
import time

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from apis.realtime_price import fetch_sina_realtime_price
from conf.conf import rules_config_path, DEFAULT_K_LIMIT
from rules.base import get_latest_n_desc_data, get_last_desc_data


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


class TurtleChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(TurtleChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = rules_config_path.joinpath('turtle.json')
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

    def _get_up_data(self, code):
        rows = get_latest_n_desc_data(code, self.m)
        data = []
        for row in rows:
            data.append(row.high)
        return data

    def _calc_up(self, code):
        data = self._get_up_data(code)
        up = max(data)
        return up

    def _get_down_data(self, code):
        rows = get_latest_n_desc_data(code, self.n)
        data = []
        for row in rows:
            data.append(row.low)
        return data

    def _calc_down(self, code):
        data = self._get_down_data(code)
        down = min(data)
        return down

    def choose(self, code):
        data = get_last_desc_data(code)
        price = max(data.open, data.close, data.high)
        up = self._calc_up(code)
        if round((abs(up - price) / price), 3) * 100 <= self.k:
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

        self.config_path = rules_config_path.joinpath('turtle.json')
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

    def _get_up_data(self, code):
        rows = get_latest_n_desc_data(code, self.m)
        data = []
        for row in rows:
            data.append(row.high)
        return data

    def _calc_up(self, code):
        data = self._get_up_data(code)
        up = max(data)
        return up

    def _get_down_data(self, code):
        rows = get_latest_n_desc_data(code, self.n)
        data = []
        for row in rows:
            data.append(row.low)
        return data

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


class Turtle:
    def __init__(self):
        self.config_path = rules_config_path.joinpath('turtle.json')
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

    def _get_up_data(self, code):
        rows = get_latest_n_desc_data(code, self.m)
        data = []
        for row in rows:
            data.append(row.high)
        return data

    def calc_up(self, code):
        data = self._get_up_data(code)
        up = max(data)
        return up

    def _get_down_data(self, code):
        rows = get_latest_n_desc_data(code, self.n)
        data = []
        for row in rows:
            data.append(row.low)
        return data

    def calc_down(self, code):
        data = self._get_down_data(code)
        down = min(data)
        return down

    def _get_batch_up_data(self, code):
        rows = get_latest_n_desc_data(code, DEFAULT_K_LIMIT)
        data = []
        for row in rows:
            data.append(row.high)
        return data[::-1]

    def calc_batch_up(self, code):
        data = self._get_batch_up_data(code)
        ups = []
        for i in range(len(data)):
            if i < self.m - 1:
                continue
            up = max(data[i - self.m + 1: i + 1])
            ups.append(up)
        _ups = [0] * self.m
        ups = _ups + ups[:-1]
        return ups

    def _get_batch_down_data(self, code):
        rows = get_latest_n_desc_data(code, DEFAULT_K_LIMIT)
        data = []
        for row in rows:
            data.append(row.low)
        return data[::-1]

    def calc_batch_down(self, code):
        data = self._get_batch_down_data(code)
        downs = []
        for i in range(len(data)):
            if i < self.n - 1:
                continue
            down = min(data[i - self.n + 1: i + 1])
            downs.append(down)
        _downs = [0] * self.n
        downs = _downs + downs[:-1]
        return downs

    def _get_batch_close_date(self, code):
        rows = get_latest_n_desc_data(code, DEFAULT_K_LIMIT)
        close = []
        date = []
        for row in rows:
            close.append(row.close)
            date.append(row.date)
        return close[::-1], date[::-1]

    def track(self, code, init_money, fee, pass_fee, tax):
        closes, dates = self._get_batch_close_date(code)
        ups = self.calc_batch_up(code)
        downs = self.calc_batch_down(code)
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
            if closes[i] >= ups[i]:
                state = 'b'
                if state != old_state:
                    buy_prices.append(closes[i])
                    buy_dates.append(dates[i])
                    buy_index.append(i)
                    old_state = state
            elif closes[i] < downs[i]:
                state = 's'
                if state != old_state:
                    sell_prices.append(closes[i])
                    sell_dates.append(dates[i])
                    sell_index.append(i)
                    old_state = state
        if len(sell_prices) < len(buy_prices):
            sell_prices.append(closes[-1])
            sell_dates.append(dates[-1])

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
            opening_index_slices.append(opening_index)
            opening_price_slices.append(opening_price)

        _return = (money - init_money) / init_money * 100
        max_drawdown = max(drawdowns)

        return _return, max_drawdown, closes, dates, \
               opening_index_slices, opening_price_slices, \
               closing_index_slices, closing_price_slices


class TurtleConfig(QDialog):
    def __init__(self, parent=None):
        super(TurtleConfig, self).__init__(parent)
        self.setWindowTitle('海龟交易策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = rules_config_path.joinpath('turtle.json')
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
