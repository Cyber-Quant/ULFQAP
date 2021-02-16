import datetime

from qtpy.QtCore import *

from strategies.common import filter_roe, filter_ltv, filter_ito, \
    filter_artr, filter_dar, get_stat_date, get_value_info


def value_choose(roe, ltv, ito, artr, dar):
    stocks = []
    date = get_stat_date()

    roe_stocks = filter_roe(roe, date)
    ltv_stocks = filter_ltv(ltv, date)
    ito_stocks = filter_ito(ito, date)
    artr_stocks = filter_artr(artr, date)
    dar_stocks = filter_dar(dar, date)

    for code in roe_stocks:
        if code in ito_stocks:
            if code in artr_stocks:
                if code in dar_stocks:
                    if code not in stocks:
                        stocks.append(code)
    return stocks


class ValueChoose(QThread):
    progress_signal = Signal(int, str, str, float, float, float, float, float)

    def __init__(self, roe, ltv, ito, artr, dar, parent=None):
        super(ValueChoose, self).__init__(parent)
        self.roe = roe
        self.ltv = ltv
        self.ito = ito
        self.artr = artr
        self.dar = dar
        self.stat_date = get_stat_date()

    def run(self):
        stocks = value_choose(self.roe, self.ltv, self.ito, self.artr, self.dar)
        step = int(len(stocks) / 100) + 1
        i = 0
        j = 0
        for stock in stocks:
            i += 1
            code, name, roe, ltv, ito, artr, dar = get_value_info(
                stock, self.stat_date)
            self.progress_signal.emit(j, code, name, roe, ltv, ito, artr, dar)
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '', 0.0, 0.0, 0.0, 0.0, 0.0)
