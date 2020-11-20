import json

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import rules_config_path, DEFAULT_K_DAYS
from rules.base import get_latest_n_desc_data


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
        股价上涨/下跌，但是DIF和DEA不跟随，即发生背离，认为可以做空/做多。
        两均线均在零轴下，快速均线从下穿过慢速均线，即认为上涨趋势。零轴上下穿则认为下跌。
        '''
        self.choose_flag = True
        self.watch_flag = False


class MACDChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(MACDChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = rules_config_path.joinpath('macd.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
        else:
            self.m = 12
            self.n = 26
            self.k = 9

    def _get_batch_close_data(self, code):
        rows = get_latest_n_desc_data(code, DEFAULT_K_DAYS)
        data = []
        for row in rows:
            data.append(row.close)
        return data[::-1]

    def _calc_ema(self, data, period):
        emas = data.copy()
        for i in range(len(data)):
            if i == 0:
                emas[i] = data[i]
            if i > 0:
                emas[i] = ((period - 1) * emas[i - 1] + 2 * data[i]) / (
                        period + 1)
        return emas

    def _calc_macd(self, data):
        fast_ema = self._calc_ema(data, self.m)
        slow_ema = self._calc_ema(data, self.n)
        dif = []
        for i, data in enumerate(fast_ema):
            dif.append(fast_ema[i] - slow_ema[i])
        dea = []
        for i, data in enumerate(dif):
            if i == 0:
                dea.append(dif[i])
            else:
                dea.append(
                    (2 * dif[i] + (self.k - 1) * dea[i - 1]) / (self.k + 1)
                )
        macd = []
        for i, data in enumerate(dea):
            macd.append(2 * (dif[i] - dea[i]))
        return macd, dif, dea

    def choose(self, code):
        prices = self._get_batch_close_data(code)
        macd, dif, dea = self._calc_macd(prices)
        if dif[-1] < 0 and dea[-1] < 0 and \
                macd[-1] >= 0 and macd[-2] < 0:
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


class MACD:
    def __init__(self):
        self.config_path = rules_config_path.joinpath('macd.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
                self.k = data['k']
        else:
            self.m = 12
            self.n = 26
            self.k = 9

    def _calc_ema(self, data, period):
        emas = data.copy()
        for i in range(len(data)):
            if i == 0:
                emas[i] = data[i]
            if i > 0:
                emas[i] = ((period - 1) * emas[i - 1] + 2 * data[i]) / (
                        period + 1)
        return emas

    def calc_macd(self, closes):
        fast_ema = self._calc_ema(closes, self.m)
        slow_ema = self._calc_ema(closes, self.n)
        dif = []
        for i, data in enumerate(fast_ema):
            dif.append(fast_ema[i] - slow_ema[i])
        dea = []
        for i, data in enumerate(dif):
            if i == 0:
                dea.append(dif[i])
            else:
                dea.append(
                    (2 * dif[i] + (self.k - 1) * dea[i - 1]) / (self.k + 1)
                )
        macd = []
        for i, data in enumerate(dea):
            macd.append(2 * (dif[i] - dea[i]))
        return macd, dif, dea


class MACDConfig(QDialog):
    def __init__(self, parent=None):
        super(MACDConfig, self).__init__(parent)
        self.setWindowTitle('MACD策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = rules_config_path.joinpath('macd.json')
        self.info = MACDInfo()

        reg = QRegExp('[0-9]+$')
        validator = QRegExpValidator()
        validator.setRegExp(reg)

        main_f_box = QFormLayout()
        self.desc = QTextEdit()
        self.desc.setReadOnly(True)
        self.desc.setText(self.info.desc)
        self.m_label = QLabel('短周期m')
        self.m_input = QLineEdit()
        self.m_input.setValidator(validator)
        self.n_label = QLabel('长周期n')
        self.n_input = QLineEdit()
        self.n_input.setValidator(validator)
        self.k_label = QLabel('DEA线周期k')
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
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = MACDConfig()
    main.show()

    sys.exit(app.exec_())
