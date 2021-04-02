import baostock as bs
import datetime

from qtpy.QtCore import *

from apis.statements import fetch_performance_express_report, \
    fetch_forecast_report, store_performance_express_report, \
    store_forecast_report
from conf.conf import FIRST_DAY_YEAR
from db.models import AStockProfitData, AStockOperationData, AStockGrowthData, \
    AStockBalanceData, AStockCashFlowData, AStockDupontData
from db.ops import create_table, drop_table


def reset_finance_data():
    drop_table(AStockProfitData)
    create_table(AStockProfitData)
    drop_table(AStockOperationData)
    create_table(AStockOperationData)
    drop_table(AStockGrowthData)
    create_table(AStockGrowthData)
    drop_table(AStockBalanceData)
    create_table(AStockBalanceData)
    drop_table(AStockCashFlowData)
    create_table(AStockCashFlowData)
    drop_table(AStockDupontData)
    create_table(AStockDupontData)


def _fetch_profit_data(code, args):
    data_list = []
    for arg in args:
        year, quarter = arg
        rs = bs.query_profit_data(code=code, year=year, quarter=quarter)
        if rs.error_code != '0' or rs.error_msg != 'success':
            return int(rs.error_code), rs.error_msg
        while (rs.error_code == '0') & rs.next():
            data = rs.get_row_data()
            if len(data) > 0:
                data_list.append(data)
    return 0, data_list


def fetch_profit_data(code):
    rows = AStockProfitData.select().where(AStockProfitData.code ==
                                           code).order_by(
        AStockProfitData.stat_date.desc())
    now = datetime.datetime.now()
    year_now = now.year
    quarter_now = int((now.month - 1) / 3) + 1

    args = []
    if rows.count() == 0:
        for year in range(FIRST_DAY_YEAR, year_now + 1):
            for quarter in range(1, 5):
                if year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    elif rows.count() > 0:
        year_start = rows[0].stat_date.year
        month = rows[0].stat_date.month
        quarter_start = int((month - 1) / 3) + 1
        for year in range(year_start, year_now + 1):
            for quarter in range(1, 5):
                if year == year_start and quarter <= quarter_start:
                    continue
                elif year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    ret, data = _fetch_profit_data(code, args)
    if ret != 0:
        return -1, data
    else:
        return 0, data


def store_profit_data(data_list):
    records = []
    for data in data_list:
        if data[3] == '':
            ROE_avg = 0.0
        else:
            ROE_avg = float(data[3])
        if data[4] == '':
            np_margin = 0.0
        else:
            np_margin = float(data[4])
        if data[5] == '':
            gp_margin = 0.0
        else:
            gp_margin = float(data[5])
        if data[6] == '':
            net_profit = 0.0
        else:
            net_profit = float(data[6])
        if data[7] == '':
            eps_TTM = 0
        else:
            eps_TTM = float(data[7])
        if data[8] == '':
            MB_revenue = 0.0
        else:
            MB_revenue = float(data[8])
        if data[9] == '':
            total_share = 0.0
        else:
            total_share = float(data[9])
        if data[10] == '':
            liqa_share = 0.0
        else:
            liqa_share = float(data[10])
        record = {
            'code': data[0],
            'pub_date': datetime.datetime.strptime(data[1], '%Y-%m-%d'),
            'stat_date': datetime.datetime.strptime(data[2], '%Y-%m-%d'),
            'ROE_avg': ROE_avg,
            'np_margin': np_margin,
            'gp_margin': gp_margin,
            'net_profit': net_profit,
            'eps_TTM': eps_TTM,
            'MB_revenue': MB_revenue,
            'total_share': total_share,
            'liqa_share': liqa_share
        }
        records.append(record)
    query = AStockProfitData.insert_many(records)
    query.execute()


def _fetch_operation_data(code, args):
    data_list = []
    for arg in args:
        year, quarter = arg
        rs = bs.query_operation_data(code=code, year=year, quarter=quarter)
        if rs.error_code != '0' or rs.error_msg != 'success':
            return int(rs.error_code), rs.error_msg
        while (rs.error_code == '0') & rs.next():
            data = rs.get_row_data()
            if len(data) > 0:
                data_list.append(data)
    return 0, data_list


def fetch_operation_data(code):
    rows = AStockOperationData.select().where(AStockOperationData.code ==
                                              code).order_by(
        AStockOperationData.stat_date.desc())
    now = datetime.datetime.now()
    year_now = now.year
    quarter_now = int((now.month - 1) / 3) + 1

    args = []
    if rows.count() == 0:
        for year in range(FIRST_DAY_YEAR, year_now + 1):
            for quarter in range(1, 5):
                if year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    elif rows.count() > 0:
        year_start = rows[0].stat_date.year
        month = rows[0].stat_date.month
        quarter_start = int((month - 1) / 3) + 1
        for year in range(year_start, year_now + 1):
            for quarter in range(1, 5):
                if year == year_start and quarter <= quarter_start:
                    continue
                elif year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    ret, data = _fetch_operation_data(code, args)
    if ret != 0:
        return -1, data
    else:
        return 0, data


def store_operation_data(data_list):
    records = []
    for data in data_list:
        if data[3] == '':
            NR_turn_ratio = 0.0
        else:
            NR_turn_ratio = float(data[3])
        if data[4] == '':
            NR_turn_days = 0.0
        else:
            NR_turn_days = float(data[4])
        if data[5] == '':
            INV_turn_ratio = 0.0
        else:
            INV_turn_ratio = float(data[5])
        if data[6] == '':
            INV_turn_days = 0.0
        else:
            INV_turn_days = float(data[6])
        if data[7] == '':
            CA_turn_ratio = 0.0
        else:
            CA_turn_ratio = float(data[7])
        if data[8] == '':
            asset_turn_ratio = 0.0
        else:
            asset_turn_ratio = float(data[8])
        record = {
            'code': data[0],
            'pub_date': datetime.datetime.strptime(data[1], '%Y-%m-%d'),
            'stat_date': datetime.datetime.strptime(data[2], '%Y-%m-%d'),
            'NR_turn_ratio': NR_turn_ratio,
            'NR_turn_days': NR_turn_days,
            'INV_turn_ratio': INV_turn_ratio,
            'INV_turn_days': INV_turn_days,
            'CA_turn_ratio': CA_turn_ratio,
            'asset_turn_ratio': asset_turn_ratio
        }
        records.append(record)
    query = AStockOperationData.insert_many(records)
    query.execute()


def _fetch_growth_data(code, args):
    data_list = []
    for arg in args:
        year, quarter = arg
        rs = bs.query_growth_data(code=code, year=year, quarter=quarter)
        if rs.error_code != '0' or rs.error_msg != 'success':
            return int(rs.error_code), rs.error_msg
        while (rs.error_code == '0') & rs.next():
            data = rs.get_row_data()
            if len(data) > 0:
                data_list.append(data)
    return 0, data_list


def fetch_growth_data(code):
    rows = AStockGrowthData.select().where(AStockGrowthData.code ==
                                           code).order_by(
        AStockGrowthData.stat_date.desc())
    now = datetime.datetime.now()
    year_now = now.year
    quarter_now = int((now.month - 1) / 3) + 1

    args = []
    if rows.count() == 0:
        for year in range(FIRST_DAY_YEAR, year_now + 1):
            for quarter in range(1, 5):
                if year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    elif rows.count() > 0:
        year_start = rows[0].stat_date.year
        month = rows[0].stat_date.month
        quarter_start = int((month - 1) / 3) + 1
        for year in range(year_start, year_now + 1):
            for quarter in range(1, 5):
                if year == year_start and quarter <= quarter_start:
                    continue
                elif year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    ret, data = _fetch_growth_data(code, args)
    if ret != 0:
        return -1, data
    else:
        return 0, data


def store_growth_data(data_list):
    records = []
    for data in data_list:
        if data[3] == '':
            YOY_equity = 0.0
        else:
            YOY_equity = float(data[3])
        if data[4] == '':
            YOY_asset = 0.0
        else:
            YOY_asset = float(data[4])
        if data[5] == '':
            YOYNI = 0.0
        else:
            YOYNI = float(data[5])
        if data[6] == '':
            YOYPNI = 0.0
        else:
            YOYPNI = float(data[6])
        record = {
            'code': data[0],
            'pub_date': datetime.datetime.strptime(data[1], '%Y-%m-%d'),
            'stat_date': datetime.datetime.strptime(data[2], '%Y-%m-%d'),
            'YOY_equity': YOY_equity,
            'YOY_asset': YOY_asset,
            'YOYNI': YOYNI,
            'YOYPNI': YOYPNI
        }
        records.append(record)
    query = AStockGrowthData.insert_many(records)
    query.execute()


def _fetch_balance_data(code, args):
    data_list = []
    for arg in args:
        year, quarter = arg
        rs = bs.query_balance_data(code=code, year=year, quarter=quarter)
        if rs.error_code != '0' or rs.error_msg != 'success':
            return int(rs.error_code), rs.error_msg
        while (rs.error_code == '0') & rs.next():
            data = rs.get_row_data()
            if len(data) > 0:
                data_list.append(data)
    return 0, data_list


def fetch_balance_data(code):
    rows = AStockBalanceData.select().where(AStockBalanceData.code ==
                                            code).order_by(
        AStockBalanceData.stat_date.desc())
    now = datetime.datetime.now()
    year_now = now.year
    quarter_now = int((now.month - 1) / 3) + 1

    args = []
    if rows.count() == 0:
        for year in range(FIRST_DAY_YEAR, year_now + 1):
            for quarter in range(1, 5):
                if year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    elif rows.count() > 0:
        year_start = rows[0].stat_date.year
        month = rows[0].stat_date.month
        quarter_start = int((month - 1) / 3) + 1
        for year in range(year_start, year_now + 1):
            for quarter in range(1, 5):
                if year == year_start and quarter <= quarter_start:
                    continue
                elif year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    ret, data = _fetch_balance_data(code, args)
    if ret != 0:
        return -1, data
    else:
        return 0, data


def store_balance_data(data_list):
    records = []
    for data in data_list:
        if data[3] == '':
            current_ratio = 0.0
        else:
            current_ratio = float(data[3])
        if data[4] == '':
            quick_ratio = 0.0
        else:
            quick_ratio = float(data[4])
        if data[5] == '':
            cash_ratio = 0.0
        else:
            cash_ratio = float(data[5])
        if data[6] == '':
            YOY_liability = 0.0
        else:
            YOY_liability = float(data[6])
        if data[7] == '':
            liability_to_asset = 0
        else:
            liability_to_asset = float(data[7])
        if data[8] == '':
            asset_to_equity = 0.0
        else:
            asset_to_equity = float(data[8])
        record = {
            'code': data[0],
            'pub_date': datetime.datetime.strptime(data[1], '%Y-%m-%d'),
            'stat_date': datetime.datetime.strptime(data[2], '%Y-%m-%d'),
            'current_ratio': current_ratio,
            'quick_ratio': quick_ratio,
            'cash_ratio': cash_ratio,
            'YOY_liability': YOY_liability,
            'liability_to_asset': liability_to_asset,
            'asset_to_equity': asset_to_equity
        }
        records.append(record)
    query = AStockBalanceData.insert_many(records)
    query.execute()


def _fetch_cash_flow_data(code, args):
    data_list = []
    for arg in args:
        year, quarter = arg
        rs = bs.query_cash_flow_data(code=code, year=year, quarter=quarter)
        if rs.error_code != '0' or rs.error_msg != 'success':
            return int(rs.error_code), rs.error_msg
        while (rs.error_code == '0') & rs.next():
            data = rs.get_row_data()
            if len(data) > 0:
                data_list.append(data)
    return 0, data_list


def fetch_cash_flow_data(code):
    rows = AStockCashFlowData.select().where(AStockCashFlowData.code ==
                                             code).order_by(
        AStockCashFlowData.stat_date.desc())
    now = datetime.datetime.now()
    year_now = now.year
    quarter_now = int((now.month - 1) / 3) + 1

    args = []
    if rows.count() == 0:
        for year in range(FIRST_DAY_YEAR, year_now + 1):
            for quarter in range(1, 5):
                if year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    elif rows.count() > 0:
        year_start = rows[0].stat_date.year
        month = rows[0].stat_date.month
        quarter_start = int((month - 1) / 3) + 1
        for year in range(year_start, year_now + 1):
            for quarter in range(1, 5):
                if year == year_start and quarter <= quarter_start:
                    continue
                elif year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    ret, data = _fetch_profit_data(code, args)
    if ret != 0:
        return -1, data
    else:
        return 0, data


def store_cash_flow_data(data_list):
    records = []
    for data in data_list:
        if data[3] == '':
            CA_to_asset = 0.0
        else:
            CA_to_asset = float(data[3])
        if data[4] == '':
            NCA_to_asset = 0.0
        else:
            NCA_to_asset = float(data[4])
        if data[5] == '':
            tangible_asset_to_asset = 0.0
        else:
            tangible_asset_to_asset = float(data[5])
        if data[6] == '':
            ebit_to_interest = 0.0
        else:
            ebit_to_interest = float(data[6])
        if data[7] == '':
            CFO_to_OR = 0
        else:
            CFO_to_OR = float(data[7])
        if data[8] == '':
            CFO_to_NP = 0.0
        else:
            CFO_to_NP = float(data[8])
        if data[9] == '':
            CFO_to_gr = 0.0
        else:
            CFO_to_gr = float(data[9])
        record = {
            'code': data[0],
            'pub_date': datetime.datetime.strptime(data[1], '%Y-%m-%d'),
            'stat_date': datetime.datetime.strptime(data[2], '%Y-%m-%d'),
            'CA_to_asset': CA_to_asset,
            'NCA_to_asset': NCA_to_asset,
            'tangible_asset_to_asset': tangible_asset_to_asset,
            'ebit_to_interest': ebit_to_interest,
            'CFO_to_OR': CFO_to_OR,
            'CFO_to_NP': CFO_to_NP,
            'CFO_to_gr': CFO_to_gr
        }
        records.append(record)
    query = AStockCashFlowData.insert_many(records)
    query.execute()


def _fetch_dupont_data(code, args):
    data_list = []
    for arg in args:
        year, quarter = arg
        rs = bs.query_dupont_data(code=code, year=year, quarter=quarter)
        if rs.error_code != '0' or rs.error_msg != 'success':
            return int(rs.error_code), rs.error_msg
        while (rs.error_code == '0') & rs.next():
            data = rs.get_row_data()
            if len(data) > 0:
                data_list.append(data)
    return 0, data_list


def fetch_dupont_data(code):
    rows = AStockDupontData.select().where(AStockDupontData.code ==
                                           code).order_by(
        AStockDupontData.stat_date.desc())
    now = datetime.datetime.now()
    year_now = now.year
    quarter_now = int((now.month - 1) / 3) + 1

    args = []
    if rows.count() == 0:
        for year in range(FIRST_DAY_YEAR, year_now + 1):
            for quarter in range(1, 5):
                if year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    elif rows.count() > 0:
        year_start = rows[0].stat_date.year
        month = rows[0].stat_date.month
        quarter_start = int((month - 1) / 3) + 1
        for year in range(year_start, year_now + 1):
            for quarter in range(1, 5):
                if year == year_start and quarter <= quarter_start:
                    continue
                elif year == year_now and quarter == quarter_now:
                    args.append((year, quarter))
                    break
                args.append((year, quarter))
    ret, data = _fetch_dupont_data(code, args)
    if ret != 0:
        return -1, data
    else:
        return 0, data


def store_dupont_data(data_list):
    records = []
    for data in data_list:
        if data[3] == '':
            dupont_ROE = 0.0
        else:
            dupont_ROE = float(data[3])
        if data[4] == '':
            dupont_asset_sto_equity = 0.0
        else:
            dupont_asset_sto_equity = float(data[4])
        if data[5] == '':
            dupont_asset_turn = 0.0
        else:
            dupont_asset_turn = float(data[5])
        if data[6] == '':
            dupont_pnitoni = 0.0
        else:
            dupont_pnitoni = float(data[6])
        if data[7] == '':
            dupont_nitogr = 0
        else:
            dupont_nitogr = float(data[7])
        if data[8] == '':
            dupont_tax_burden = 0.0
        else:
            dupont_tax_burden = float(data[8])
        if data[9] == '':
            dupont_intburden = 0.0
        else:
            dupont_intburden = float(data[9])
        if data[10] == '':
            dupont_ebittogr = 0.0
        else:
            dupont_ebittogr = float(data[10])
        record = {
            'code': data[0],
            'pub_date': datetime.datetime.strptime(data[1], '%Y-%m-%d'),
            'stat_date': datetime.datetime.strptime(data[2], '%Y-%m-%d'),
            'dupont_ROE': dupont_ROE,
            'dupont_asset_sto_equity': dupont_asset_sto_equity,
            'dupont_asset_turn': dupont_asset_turn,
            'dupont_pnitoni': dupont_pnitoni,
            'dupont_nitogr': dupont_nitogr,
            'dupont_tax_burden': dupont_tax_burden,
            'dupont_intburden': dupont_intburden,
            'dupont_ebittogr': dupont_ebittogr
        }
        records.append(record)
    query = AStockDupontData.insert_many(records)
    query.execute()


class FetchFinancialData(QThread):
    sig_fetch_financial = Signal(int)
    sig_fetch_financial_done = Signal()
    err_signal = Signal(str)

    def __init__(self, e_date, code_list, parent=None):
        super(FetchFinancialData, self).__init__(parent)
        self.e_date = e_date
        self.stock_code_list = code_list

    def run(self):
        lg = bs.login()
        if lg.error_code != '0' or lg.error_msg != 'success':
            return lg.error_msg

        self.sig_fetch_financial.emit(1)
        stock_num = len(self.stock_code_list)
        total_num = int(stock_num / 100 * 110)
        step = int(total_num / 100)
        i = 0
        j = 0
        for code in self.stock_code_list:
            i += 1
            ret, data = fetch_profit_data(code)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            store_profit_data(data)

            ret, data = fetch_operation_data(code)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            store_operation_data(data)

            ret, data = fetch_growth_data(code)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            store_growth_data(data)

            ret, data = fetch_balance_data(code)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            store_balance_data(data)

            ret, data = fetch_cash_flow_data(code)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            store_cash_flow_data(data)

            ret, data = fetch_dupont_data(code)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            store_dupont_data(data)

            ret, data = fetch_performance_express_report(code, self.e_date)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            store_performance_express_report(data)

            ret, data = fetch_forecast_report(code, self.e_date)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            store_forecast_report(data)
            if i % step == 0:
                j += 1
                self.sig_fetch_financial.emit(j)
        self.sig_fetch_financial_done.emit()
        bs.logout()
        return True
