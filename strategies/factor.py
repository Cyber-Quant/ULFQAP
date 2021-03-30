import baostock as bs
import datetime
import json

from qtpy.QtCore import *

from apis.code_index import fetch_last_trading_day
from strategies.common import filter_pe, filter_roe, filter_cmv, filter_ito, \
    filter_artr, filter_dar, filter_ltv, filter_op, filter_last_turn_over, \
    filter_last_percent_change, get_stat_date, get_factor_info, sort_pe, \
    sort_roe, sort_cmv, sort_ito, sort_artr, sort_dar, sort_op, \
    sort_last_turn_over, sort_last_percent_change


def factor_choose(strategy):
    lg = bs.login()
    if lg.error_code != '0' or lg.error_msg != 'success':
        return lg.error_msg
    date_str = fetch_last_trading_day()
    bs.logout()
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    stat_date = get_stat_date()

    pe_filter_flag = False
    roe_filter_flag = False
    cmv_filter_flag = False
    ito_filter_flag = False
    artr_filter_flag = False
    dar_filter_flag = False
    ltv_filter_flag = False
    op_filter_flag = False
    last_turn_over_filter_flag = False
    last_percent_change_filter_flag = False
    for item in strategy['filter']:
        if item['key'] == 'PE':
            pe_filter_flag = True
            pe_cond = item['condition']
            pe_v = item['value']
            if '区间' in item['condition']:
                pe_v2 = item['value2']
            else:
                pe_v2 = 0
        if item['key'] == 'ROE':
            roe_filter_flag = True
            roe_cond = item['condition']
            roe_v = item['value']
            if '区间' in item['condition']:
                roe_v2 = item['value2']
            else:
                roe_v2 = 0
        if item['key'] == '流通市值':
            cmv_filter_flag = True
            cmv_cond = item['condition']
            cmv_v = item['value']
            if '区间' in item['condition']:
                cmv_v2 = item['value2']
            else:
                cmv_v2 = 0
        if item['key'] == '存货率':
            ito_filter_flag = True
            ito_cond = item['condition']
            ito_v = item['value']
            if '区间' in item['condition']:
                ito_v2 = item['value2']
            else:
                ito_v2 = 0
        if item['key'] == '应收帐款率':
            artr_filter_flag = True
            artr_cond = item['condition']
            artr_v = item['value']
            if '区间' in item['condition']:
                artr_v2 = item['value2']
            else:
                artr_v2 = 0
        if item['key'] == '资产负债率':
            dar_filter_flag = True
            dar_cond = item['condition']
            dar_v = item['value']
            if '区间' in item['condition']:
                dar_v2 = item['value2']
            else:
                dar_v2 = 0
        if item['key'] == '开盘价':
            op_filter_flag = True
            op_cond = item['condition']
            op_v = item['value']
            if '区间' in item['condition']:
                op_v2 = item['value2']
            else:
                op_v2 = 0
        if item['key'] == '昨换手率':
            last_turn_over_filter_flag = True
            last_turn_over_cond = item['condition']
            last_turn_over_v = item['value']
            if '区间' in item['condition']:
                last_turn_over_v2 = item['value2']
            else:
                last_turn_over_v2 = 0
        if item['key'] == '昨涨跌幅':
            last_percent_change_filter_flag = True
            last_percent_change_cond = item['condition']
            last_percent_change_v = item['value']
            if '区间' in item['condition']:
                last_percent_change_v2 = item['value2']
            else:
                last_percent_change_v2 = 0

    pe_flag = False
    roe_flag = False
    cmv_flag = False
    ito_flag = False
    artr_flag = False
    dar_flag = False
    op_flag = False
    last_turn_over_flag = False
    last_percent_change_flag = False
    if pe_filter_flag:
        pe_flag = True
        pe_stocks = filter_pe(pe_v, pe_cond, pe_v2, date)
    if roe_filter_flag:
        roe_flag = True
        roe_stocks = filter_roe(roe_v, roe_cond, roe_v2, stat_date)
    if cmv_filter_flag:
        cmv_flag = True
        cmv_stocks = filter_cmv(cmv_v, cmv_cond, cmv_v2, stat_date)
    if ito_filter_flag:
        ito_flag = True
        ito_stocks = filter_ito(ito_v, ito_cond, ito_v2, stat_date)
    if artr_filter_flag:
        artr_flag = True
        artr_stocks = filter_artr(artr_v, artr_cond, artr_v2, stat_date)
    if dar_filter_flag:
        dar_flag = True
        dar_stocks = filter_dar(dar_v, dar_cond, dar_v2, stat_date)
    if op_filter_flag:
        op_flag = True
        op_stocks = filter_op(op_v, op_cond, op_v2, date)
    if last_turn_over_filter_flag:
        last_turn_over_flag = True
        last_turn_over_stocks = filter_last_turn_over(last_turn_over_v,
                                                      last_turn_over_cond,
                                                      last_turn_over_v2,
                                                      date)
    if last_percent_change_filter_flag:
        last_percent_change_flag = True
        last_percent_change_stocks = filter_last_percent_change(
            last_percent_change_v,
            last_percent_change_cond,
            last_percent_change_v2,
            date)

    stocks = []
    if pe_flag:
        if len(pe_stocks) == 0:
            return []
        stocks += pe_stocks
    if roe_flag:
        if not pe_flag:
            if len(roe_stocks) == 0:
                return []
            stocks += roe_stocks
        else:
            _stocks = stocks
            stocks = []
            for code in roe_stocks:
                if code in _stocks:
                    stocks.append(code)
    if cmv_flag:
        if not pe_flag or not roe_flag:
            if len(cmv_stocks) == 0:
                return []
            stocks += cmv_stocks
        else:
            _stocks = stocks
            stocks = []
            for code in cmv_stocks:
                if code in _stocks:
                    stocks.append(code)
    if ito_flag:
        if not pe_flag or not roe_flag or not cmv_flag:
            if len(ito_stocks) == 0:
                return []
            stocks += ito_stocks
        else:
            _stocks = stocks
            stocks = []
            for code in ito_stocks:
                if code in _stocks:
                    stocks.append(code)
    if artr_flag:
        if not pe_flag or not roe_flag or not cmv_flag or not ito_flag:
            if len(artr_stocks) == 0:
                return []
            stocks += artr_stocks
        else:
            _stocks = stocks
            stocks = []
            for code in artr_stocks:
                if code in _stocks:
                    stocks.append(code)
    if dar_flag:
        if not pe_flag or not roe_flag or not cmv_flag or not ito_flag \
                or not artr_flag:
            if len(dar_stocks) == 0:
                return []
            stocks += dar_stocks
        else:
            _stocks = stocks
            stocks = []
            for code in dar_stocks:
                if code in _stocks:
                    stocks.append(code)
    if op_flag:
        if not pe_flag or not roe_flag or not cmv_flag or not ito_flag \
                or not artr_flag or not dar_flag:
            if len(op_stocks) == 0:
                return []
            stocks += op_stocks
        else:
            _stocks = stocks
            stocks = []
            for code in op_stocks:
                if code in _stocks:
                    stocks.append(code)
    if last_turn_over_flag:
        if not pe_flag or not roe_flag or not cmv_flag or not ito_flag \
                or not artr_flag or not dar_flag or not op_flag:
            if len(last_turn_over_stocks) == 0:
                return []
            stocks += last_turn_over_stocks
        else:
            _stocks = stocks
            stocks = []
            for code in last_turn_over_stocks:
                if code in _stocks:
                    stocks.append(code)
    if last_percent_change_flag:
        if not pe_flag or not roe_flag or not cmv_flag or not ito_flag \
                or not artr_flag or not dar_flag or not op_flag \
                or not last_turn_over_flag:
            if len(last_percent_change_stocks) == 0:
                return []
            stocks += last_percent_change_stocks
        else:
            _stocks = stocks
            stocks = []
            for code in last_percent_change_stocks:
                if code in _stocks:
                    stocks.append(code)
    return stocks


def sort(codes, strategy):
    stocks = []
    for codes in codes:
        code, name, pe, roe, cmv, ito, artr, dar, ltv, op, turn, pc = \
            get_factor_info(codes)
        stock = {
            'code': code,
            'name': name,
            'pe': pe,
            'roe': roe,
            'cmv': cmv,
            'ito': ito,
            'artr': artr,
            'dar': dar,
            'ltv': ltv,
            'op': op,
            'turn': turn,
            'pc': pc
        }
        stocks.append(stock)

    pe_sort_flag = False
    roe_sort_flag = False
    cmv_sort_flag = False
    ito_sort_flag = False
    artr_sort_flag = False
    dar_sort_flag = False
    ltv_sort_flag = False
    op_sort_flag = False
    last_turn_over_sort_flag = False
    last_percent_change_sort_flag = False
    weights = 0
    for item in strategy['sort']:
        if item['key'] == 'PE':
            pe_sort_flag = True
            pe_cond = item['condition']
            pe_v = item['value']
            weights += pe_v
            pe_stocks = sort_pe(stocks, pe_cond)
        if item['key'] == 'ROE':
            roe_sort_flag = True
            roe_cond = item['condition']
            roe_v = item['value']
            weights += roe_v
            roe_stocks = sort_roe(stocks, roe_cond)
        if item['key'] == '流通市值':
            cmv_sort_flag = True
            cmv_cond = item['condition']
            cmv_v = item['value']
            weights += cmv_v
            cmv_stocks = sort_cmv(stocks, cmv_cond)
        if item['key'] == '存货率':
            ito_sort_flag = True
            ito_cond = item['condition']
            ito_v = item['value']
            weights += ito_v
            ito_stocks = sort_ito(stocks, ito_cond)
        if item['key'] == '应收帐款率':
            artr_sort_flag = True
            artr_cond = item['condition']
            artr_v = item['value']
            weights += artr_v
            artr_stocks = sort_artr(stocks, artr_cond)
        if item['key'] == '资产负债率':
            dar_sort_flag = True
            dar_cond = item['condition']
            dar_v = item['value']
            weights += dar_v
            dar_stocks = sort_dar(stocks, dar_cond)
        if item['key'] == '开盘价':
            op_sort_flag = True
            op_cond = item['condition']
            op_v = item['value']
            weights += op_v
            op_stocks = sort_op(stocks, op_cond)
        if item['key'] == '昨换手率':
            last_turn_over_sort_flag = True
            last_turn_over_cond = item['condition']
            last_turn_over_v = item['value']
            weights += last_turn_over_v
            last_turn_over_stocks = sort_last_turn_over(stocks,
                                                        last_turn_over_cond)
        if item['key'] == '昨涨跌幅':
            last_percent_change_sort_flag = True
            last_percent_change_cond = item['condition']
            last_percent_change_v = item['value']
            weights += last_percent_change_v
            last_percent_change_stocks = sort_last_percent_change(
                stocks,
                last_percent_change_cond)

    pe_score_flag = False
    roe_score_flag = False
    cmv_score_flag = False
    ito_score_flag = False
    artr_score_flag = False
    dar_score_flag = False
    op_score_flag = False
    last_turn_over_score_flag = False
    last_percent_change_score_flag = False
    if pe_sort_flag:
        pe_score_flag = True
        pe_scores = {}
        for i, stock in enumerate(stocks):
            code = stock['code']
            pe_scores[code] = pe_v / weights * (i + 1)
    if roe_sort_flag:
        roe_score_flag = True
        roe_scores = {}
        for i, stock in enumerate(stocks):
            code = stock['code']
            roe_scores[code] = roe_v / weights * (i + 1)
    if cmv_sort_flag:
        cmv_score_flag = True
        cmv_scores = {}
        for i, stock in enumerate(stocks):
            code = stock['code']
            cmv_scores[code] = cmv_v / weights * (i + 1)
    if ito_sort_flag:
        ito_score_flag = True
        ito_scores = {}
        for i, stock in enumerate(stocks):
            code = stock['code']
            ito_scores[code] = ito_v / weights * (i + 1)
    if artr_sort_flag:
        artr_score_flag = True
        artr_scores = {}
        for i, stock in enumerate(stocks):
            code = stock['code']
            artr_scores[code] = artr_v / weights * (i + 1)
    if dar_sort_flag:
        dar_score_flag = True
        dar_scores = {}
        for i, stock in enumerate(stocks):
            code = stock['code']
            dar_scores[code] = dar_v / weights * (i + 1)
    if op_sort_flag:
        op_score_flag = True
        op_scores = {}
        for i, stock in enumerate(stocks):
            code = stock['code']
            op_scores[code] = op_v / weights * (i + 1)
    if last_turn_over_sort_flag:
        last_turn_over_score_flag = True
        last_turn_over_scores = {}
        for i, stock in enumerate(stocks):
            code = stock['code']
            last_turn_over_scores[code] = last_turn_over_v / weights * (i + 1)
    if last_percent_change_sort_flag:
        last_percent_change_score_flag = True
        last_percent_change_scores = {}
        for i, stock in enumerate(stocks):
            code = stock['code']
            last_percent_change_scores[
                code] = last_percent_change_v / weights * (i + 1)

    stocks = {}
    for code in codes:
        score = 0
        if pe_score_flag:
            score += pe_scores[code]
        if roe_score_flag:
            score += roe_scores[code]
        if cmv_score_flag:
            score += cmv_scores[code]
        if ito_score_flag:
            score += ito_scores[code]
        if artr_score_flag:
            score += artr_scores[code]
        if dar_score_flag:
            score += dar_scores[code]
        if op_score_flag:
            score += op_scores[code]
        if last_turn_over_score_flag:
            score += last_turn_over_scores[code]
        if last_percent_change_score_flag:
            score += last_percent_change_scores[code]
        stocks[code] = score
    stocks.sort(key=lambda x: x['score'], reverse=False)
    return stocks


class FactorChoose(QThread):
    progress_signal = Signal(int, str, str, float, float, float, float, float,
                             float, float, float, float, float, float)

    def __init__(self, strategy, parent=None):
        super(FactorChoose, self).__init__(parent)
        self.strategy = strategy
        self.stat_date = get_stat_date()

    def run(self):
        codes = factor_choose(self.strategy)
        scores = sort(codes, self.strategy)
        step = int(len(codes) / 100) + 1
        i = 0
        j = 0
        for code in codes:
            i += 1
            code, name, pe, roe, cmv, ito, artr, dar, ltv, op, turn, pc = \
                get_factor_info(code)
            score = scores[code]
            self.progress_signal.emit(j, code, name, score, pe, roe, cmv, ito,
                                      artr, dar, ltv, op, turn, pc)
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0, 0.0)
