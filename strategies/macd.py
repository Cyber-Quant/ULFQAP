import datetime
import json

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import shape_strategies_config_path
from strategies.common import get_latest_batch_data, calc_batch_macd, calc_wpct


class MACDInfo:
    def __init__(self):
        self.name = 'MACD'
        self.desc = '''
        MACD
        快速EMA：12(m)日指数平滑移动平均线
        慢速EMA：26(n)日指数平滑移动平均线
        DIF线：快速EMA - 慢速EMA
        DEA线：9(k)日DIF线的指数平滑移动平均线
        MACD柱：2倍DIF线与DEA线的差，红绿柱
        股价上涨/下跌，但是MACD红绿柱不跟随，即发生背离，认为可以做空/做多。
        DIF上穿过DEA，金叉，即认为上涨趋势。下穿则认为下跌。
        '''
        self.choose_flag = True
        self.watch_flag = False


class MACD:
    def __init__(self):
        self.config_path = shape_strategies_config_path.joinpath('macd.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
                self.golden_cross = data['golden_cross']
                self.divergence = data['divergence']
        else:
            self.m = 12
            self.n = 26
            self.k = 9
            self.golden_cross = False
            self.divergence = True

    def calc_macd(self, closes):
        macd, dif, dea = calc_batch_macd(closes, self.m, self.n, self.k)
        return macd, dif, dea

    def backtest(self, code, s_date, e_date, init_money, fee, pass_fee, tax):
        dates, opens, closes, highs, lows, volumes, amount, turn, pct_chg, \
        ma_price, ma_volume = get_latest_batch_data(code, s_date=s_date,
                                                    e_date=e_date)
        macd, dif, dea = self.calc_macd(closes)
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
            if self.divergence:
                if dif[i - 1] > 0 and dif[i - 2] > 0 \
                        and dea[i - 1] > 0 and dea[i - 2] > 0 \
                        and macd[i - 1] > macd[i - 2] > 0 \
                        and closes[i - 1] < closes[i - 2]:
                    state = 'b'
                    if state != old_state:
                        buy_prices.append(closes[i])
                        buy_dates.append(dates[i])
                        buy_index.append(i)
                        old_state = state
                elif macd[i - 1] < macd[i - 2] \
                        and closes[i - 1] > closes[i - 2]:
                    state = 's'
                    if state != old_state:
                        sell_prices.append(closes[i])
                        sell_dates.append(dates[i])
                        sell_index.append(i)
                        old_state = state
            elif self.golden_cross:
                if dif[i - 1] > 0 and dif[i - 2] > 0 and dif[i - 3] > 0 \
                        and dea[i - 1] > 0 and dea[i - 2] > 0 \
                        and dea[i - 3] > 0 \
                        and macd[i - 1] > 0 > macd[i - 3]:
                    state = 'b'
                    if state != old_state:
                        buy_prices.append(closes[i])
                        buy_dates.append(dates[i])
                        buy_index.append(i)
                        old_state = state
                elif macd[i - 1] < 0 < macd[i - 3]:
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
        macd, dif, dea = self.calc_macd(close)
        if self.divergence:
            if dif[-1] > 0 and dif[-2] > 0 and dea[-1] > 0 and dea[-2] > 0 \
                    and macd[-1] > macd[-2] > 0 and close[-1] < close[-2]:
                return True
        elif self.golden_cross:
            if dif[-1] > 0 and dif[-2] > 0 and dif[-3] > 0 \
                    and dea[-1] > 0 and dea[-2] > 0 and dea[-3] > 0 \
                    and macd[-1] > 0 > macd[-3]:
                return True
        else:
            return False


class MACDBacktest(QThread):
    progress_signal = Signal(int, str, str, float, float, float)

    def __init__(self, stocks, s_date, e_date, init_money, fee, pass_fee, tax,
                 parent=None):
        super(MACDBacktest, self).__init__(parent)
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
        macd = MACD()
        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            wpct, _return, max_drawdown, \
            opens, closes, highs, lows, volumes, dates, \
            opening_index_slices, opening_price_slices, \
            closing_index_slices, closing_price_slices = \
                macd.backtest(code, self.s_date, self.e_date, self.init_money,
                              self.fee, self.pass_fee, self.tax)
            self.progress_signal.emit(j, code, self.names[i - 1],
                                      wpct, _return, max_drawdown)
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '', 0.0, 0.0, 0.0)


class MACDChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(MACDChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

    def run(self):
        macd = MACD()

        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            ret = macd.choose(code)
            if not ret:
                continue
            self.progress_signal.emit(j, code, self.names[i - 1])
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '')


# TODO: line color
class MACDConfig(QDialog):
    def __init__(self, parent=None):
        super(MACDConfig, self).__init__(parent)
        self.setWindowTitle('MACD策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = shape_strategies_config_path.joinpath('macd.json')
        self.info = MACDInfo()

        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
                self.golden_cross = data['golden_cross']
                self.divergence = data['divergence']
        else:
            self.m = 12
            self.n = 26
            self.k = 9
            self.golden_cross = False
            self.divergence = True

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
        self.k_label = QLabel('DEA线周期k')
        self.k_input = QLineEdit(str(self.k))
        self.k_input.setValidator(validator)
        self.golden_cross_check = QCheckBox('金叉')
        if self.golden_cross:
            self.golden_cross_check.setChecked(True)
        else:
            self.golden_cross_check.setChecked(False)
        self.divergence_check = QCheckBox('背离')
        if self.divergence:
            self.divergence_check.setChecked(True)
        else:
            self.divergence_check.setChecked(False)
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_f_box.addRow(self.desc)
        main_f_box.addRow(self.m_label, self.m_input)
        main_f_box.addRow(self.n_label, self.n_input)
        main_f_box.addRow(self.k_label, self.k_input)
        main_f_box.addRow(self.golden_cross_check)
        main_f_box.addRow(self.divergence_check)
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
        if self.divergence_check.isChecked():
            data['divergence'] = True
        else:
            data['divergence'] = False
        if self.golden_cross_check.isChecked():
            data['golden_cross'] = True
        else:
            data['golden_cross'] = False
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = MACDConfig()
    main.show()

    sys.exit(app.exec_())
