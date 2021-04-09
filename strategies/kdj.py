import datetime
import json

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from conf.conf import shape_strategies_config_path
from strategies.common import get_latest_batch_data, calc_wpct


class KDJInfo:
    def __init__(self):
        self.name = 'KDJ'
        self.desc = '''
        KDJ指数
        9(m)日RSV: (第9(m)日收盘价 - 9(m)日最低价) / (9(m)日最高价 - 9(m)日最低价) * 100
        快线K: RSV的9(m)日周期平均值
        慢线D: K的9(m)日周期平均值
        超快线/确认线J: 3*K - 2*D
        KD小于20，超卖，金叉，做多。KD大于80，超买，并且死叉，做空。
        '''
        self.choose_flag = True
        self.watch_flag = False


class KDJ:
    def __init__(self):
        self.config_path = shape_strategies_config_path.joinpath('kdj.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
        else:
            self.m = 9

    def calc_kdj(self, closes, highs, lows):
        _lows = []
        _highs = []
        for i, data in enumerate(closes):
            if i < self.m:
                continue
            _lows.append(min(lows[i - self.m + 1:i + 1]))
            _highs.append(max(highs[i - self.m + 1:i + 1]))
        __lows = [0] * self.m
        __highs = [0] * self.m
        _lows = __lows + _lows
        _highs = __highs + _highs
        rsv = []
        for i, close in enumerate(closes):
            if i < self.m:
                continue
            # When the stock is suspend, the ohlc keep the same value
            # Save the same prices
            _diff = _highs[i] - _lows[i]
            if _diff == 0:
                _diff = 0.01
            rsv.append((closes[i] - _lows[i]) / _diff * 100)
        _rsv = [0] * self.m
        rsv = _rsv + rsv
        k = []
        d = []
        j = []
        for i, data in enumerate(rsv):
            if i <= self.m:
                k.append(50)
                d.append(50)
                j.append(50)
                continue
            _k = 2 / 3 * k[i - 1] + 1 / 3 * rsv[i]
            _d = 2 / 3 * d[i - 1] + 1 / 3 * _k
            k.append(_k)
            d.append(_d)
            j.append(3 * _k - 2 * _d)

        return k, d, j

    def backtest(self, code, s_date, e_date, init_money, fee, pass_fee, tax):
        dates, opens, closes, highs, lows, volumes, amount, turn, pct_chg, \
        ma_price, ma_volume = get_latest_batch_data(code, s_date=s_date,
                                                    e_date=e_date)
        k, d, j = self.calc_kdj(closes, highs, lows)
        start = self.m
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
            if k[i] < 20 and d[i] < 20 and k[i - 1] < d[i - 1] and k[i] >= d[i]:
                state = 'b'
                if state != old_state:
                    buy_prices.append(closes[i])
                    buy_dates.append(dates[i])
                    buy_index.append(i)
                    old_state = state
            elif k[i] > 80 and d[i] > 80 and \
                    k[i - 1] >= d[i - 1] and k[i] < d[i]:
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
        date, _open, close, high, low, volume, amount, turn, pct_chg, \
        ma_price, ma_volume = \
            get_latest_batch_data(code)
        k, d, j = self.calc_kdj(close, high, low)
        if (k[-1] < 20 and d[-1] < 20) and (k[-1] >= d[-1] and k[-3] < d[-3]):
            return True
        else:
            return False


class KDJBacktest(QThread):
    progress_signal = Signal(int, str, str, float, float, float)

    def __init__(self, stocks, s_date, e_date, init_money, fee, pass_fee, tax,
                 parent=None):
        super(KDJBacktest, self).__init__(parent)
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
        kdj = KDJ()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            wpct, _return, max_drawdown, \
            opens, closes, highs, lows, volumes, dates, \
            opening_index_slices, opening_price_slices, \
            closing_index_slices, closing_price_slices = \
                kdj.backtest(code, self.s_date, self.e_date, self.init_money,
                             self.fee, self.pass_fee, self.tax)
            self.progress_signal.emit(j, code, self.names[i - 1],
                                      wpct, _return, max_drawdown)
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '', 0.0, 0.0, 0.0)


class KDJChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(KDJChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

    def run(self):
        kdj = KDJ()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            ret = kdj.choose(code)
            if not ret:
                continue
            self.progress_signal.emit(j, code, self.names[i - 1])
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '')


# TODO: line color, different usage of this strategy
class KDJConfig(QDialog):
    def __init__(self, parent=None):
        super(KDJConfig, self).__init__(parent)
        self.setWindowTitle('KDJ策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = shape_strategies_config_path.joinpath('kdj.json')
        self.info = KDJInfo()

        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
        else:
            self.m = 9

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
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_f_box.addRow(self.desc)
        main_f_box.addRow(self.m_label, self.m_input)
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
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = KDJConfig()
    main.show()

    sys.exit(app.exec_())
