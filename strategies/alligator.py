import datetime
import json

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import shape_strategies_config_path
from strategies.common import calc_batch_smma, calc_wpct, get_latest_batch_data


class AlligatorInfo:
    def __init__(self):
        self.name = 'Alligator'
        self.desc = '''
        上唇线是5(m)日SMMA向未来延后3(i)天，用绿线绘制；
        牙齿线是8(n)日SMMA向未来延后5(j)天，用红线绘制；
        下颚线是13(g)日SMMA向未来延后8(k)天，用蓝色绘制。
        绿线>红线>蓝线，市场处于上涨阶段
        绿线<红线<蓝线，市场处于下跌阶段
        '''
        self.choose_flag = True
        self.watch_flag = False


class Alligator:
    def __init__(self):
        self.config_path = shape_strategies_config_path.joinpath('alligator.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.g = data['g']
                self.i = data['i']
                self.j = data['j']
                self.k = data['k']
        else:
            self.m = 5
            self.n = 8
            self.g = 13
            self.i = 3
            self.j = 5
            self.k = 8

    def calc_batch_ups(self, close):
        if len(close) < self.m:
            return []
        up = calc_batch_smma(close, self.m)
        v = up[0]
        for i in range(self.i):
            up.pop()
            up.insert(0, v)
        return up

    def calc_batch_middles(self, close):
        if len(close) < self.n:
            return []
        middle = calc_batch_smma(close, self.n)
        v = middle[0]
        for i in range(self.j):
            middle.pop()
            middle.insert(0, v)
        return middle

    def calc_batch_downs(self, close):
        if len(close) < self.g:
            return []
        down = calc_batch_smma(close, self.g)
        v = down[0]
        for i in range(self.k):
            down.pop()
            down.insert(0, v)
        return down

    def _backtest(self, up, middle, down, state):
        if len(down) < max(self.i, self.j, self.k):
            return False

        if up > middle > down:
            return 'b'
        elif state == 'b':
            return 's'

    def backtest(self, code, s_date, e_date, init_money, fee, pass_fee, tax):
        dates, opens, closes, highs, lows, volumes, amount, turn, pct_chg, \
        ma_price, ma_volume = get_latest_batch_data(code, s_date=s_date,
                                                    e_date=e_date)
        ups = self.calc_batch_ups(closes)
        middles = self.calc_batch_middles(closes)
        downs = self.calc_batch_downs(closes)
        start = max(self.m, self.n, self.g)
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

            up = ups[i]
            middle = middles[i]
            down = downs[i]
            ret = self._backtest(up, middle, down, old_state)
            if ret == 'b':
                state = 'b'
                if state != old_state:
                    buy_prices.append(closes[i])
                    buy_dates.append(dates[i])
                    buy_index.append(i)
                    old_state = state
            elif ret == 's':
                state = 's'
                if state != old_state:
                    sell_prices.append(closes[i])
                    sell_dates.append(dates[i])
                    sell_index.append(i)
                    old_state = state
            else:
                continue

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
        up = self.calc_batch_ups(closes)
        middle = self.calc_batch_middles(closes)
        down = self.calc_batch_downs(closes)

        if len(closes) < max(self.m, self.n, self.g) + max(self.i, self.j,
                                                           self.k):
            return False

        if up[-1] > middle[-1] >= down[-1] and up[-5] < middle[-5] < down[-5]:
            return True
        else:
            return False


class AlligatorBacktest(QThread):
    progress_signal = Signal(int, str, str, float, float, float)

    def __init__(self, stocks, s_date, e_date, init_money, fee, pass_fee, tax,
                 parent=None):
        super(AlligatorBacktest, self).__init__(parent)
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
        alligator = Alligator()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            wpct, _return, max_drawdown, \
            opens, closes, highs, lows, volumes, dates, \
            opening_index_slices, opening_price_slices, \
            closing_index_slices, closing_price_slices = \
                alligator.backtest(code, self.s_date, self.e_date,
                                   self.init_money,
                                   self.fee, self.pass_fee, self.tax)
            self.progress_signal.emit(j, code, self.names[i - 1],
                                      wpct, _return, max_drawdown)
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '', 0.0, 0.0, 0.0)


class AlligatorChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(AlligatorChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

    def run(self):
        alligator = Alligator()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            ret = alligator.choose(code)
            if not ret:
                continue
            self.progress_signal.emit(j, code, self.names[i - 1])
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '')


# TODO: line color
class AlligatorConfig(QDialog):
    def __init__(self, parent=None):
        super(AlligatorConfig, self).__init__(parent)
        self.setWindowTitle('Alligator策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = shape_strategies_config_path.joinpath('alligator.json')
        self.info = AlligatorInfo()

        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.g = data['g']
                self.i = data['i']
                self.j = data['j']
                self.k = data['k']
        else:
            self.m = 5
            self.n = 8
            self.g = 13
            self.i = 3
            self.j = 5
            self.k = 8

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
        self.n_label = QLabel('周期n')
        self.n_input = QLineEdit(str(self.n))
        self.n_input.setValidator(validator)
        self.g_label = QLabel('周期g')
        self.g_input = QLineEdit(str(self.g))
        self.g_input.setValidator(validator)
        self.i_label = QLabel('偏移i')
        self.i_input = QLineEdit(str(self.i))
        self.i_input.setValidator(validator)
        self.j_label = QLabel('偏移i')
        self.j_input = QLineEdit(str(self.j))
        self.j_input.setValidator(validator)
        self.k_label = QLabel('偏移k')
        self.k_input = QLineEdit(str(self.k))
        self.k_input.setValidator(validator)
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_f_box.addRow(self.desc)
        main_f_box.addRow(self.m_label, self.m_input)
        main_f_box.addRow(self.n_label, self.n_input)
        main_f_box.addRow(self.g_label, self.g_input)
        main_f_box.addRow(self.i_label, self.i_input)
        main_f_box.addRow(self.j_label, self.j_input)
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
        data['g'] = int(self.g_input.text())
        data['i'] = int(self.i_input.text())
        data['j'] = int(self.j_input.text())
        data['k'] = int(self.k_input.text())
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = AlligatorConfig()
    main.show()

    sys.exit(app.exec_())
