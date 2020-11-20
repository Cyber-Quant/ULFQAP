import baostock as bs
import datetime

from qtpy.QtCore import *

from apis.stock_info import AStockInfo, fetch_all_code, \
    reset_stock_info, save_last_updated_date, fetch_last_trading_day, \
    fetch_stock_info
from db.models import AStockDayLine
from db.ops import create_table, drop_table


def reset_k_line_data():
    drop_table(AStockDayLine)
    create_table(AStockDayLine)


def _fetch_day_line_data(code, start_date, end_date):
    rs = bs.query_history_k_data_plus(code,
                                      'date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST',
                                      start_date=start_date,
                                      end_date=end_date,
                                      frequency='d', adjustflag='3')
    if rs.error_code != '0' or rs.error_msg != 'success':
        return int(rs.error_code), rs.error_msg

    data_list = []
    while (rs.error_code == '0') & rs.next():
        data = rs.get_row_data()
        if len(data) > 0:
            data_list.append(data)
    return 0, data_list


# TODO Using asc()/desc().get() to reduce SQL query.
def fetch_day_line_data(code, start_date, end_date):
    charts = AStockDayLine.select().where(AStockDayLine.code == code).order_by(
        AStockDayLine.date.asc())
    if charts.count() == 0:
        ret, data = _fetch_day_line_data(code, start_date, end_date)
        if ret != 0:
            return -1, data
        else:
            return 0, data

    data_list = []
    if datetime.datetime.strptime(start_date, '%Y-%m-%d') < charts[0].date:
        new_end_date = charts[0].date + datetime.timedelta(-1)
        new_end_date_str = new_end_date.strftime('%Y-%m-%d')
        ret, older_data = _fetch_day_line_data(code, start_date,
                                               new_end_date_str)
        if ret != 0:
            return -1, older_data
        data_list = data_list + older_data
    if datetime.datetime.strptime(end_date, '%Y-%m-%d') > charts[-1].date:
        new_start_date = charts[-1].date + datetime.timedelta(1)
        new_start_date_str = new_start_date.strftime('%Y-%m-%d')
        ret, newer_data = _fetch_day_line_data(code, new_start_date_str,
                                               end_date)
        if ret != 0:
            return -1, newer_data
        data_list = data_list + newer_data
    return 0, data_list


def store_day_line_data(data_list):
    records = []
    for data in data_list:
        if data[2] == '':
            _open = 0.0
        else:
            _open = float(data[2])
        if data[3] == '':
            high = 0.0
        else:
            high = float(data[3])
        if data[4] == '':
            low = 0.0
        else:
            low = float(data[4])
        if data[5] == '':
            close = 0.0
        else:
            close = float(data[5])
        if data[6] == '':
            pre_close = 0.0
        else:
            pre_close = float(data[6])
        if data[7] == '':
            volume = 0
        else:
            volume = int(data[7])
        if data[8] == '':
            amount = 0.0
        else:
            amount = float(data[8])
        if data[10] == '':
            turn = 0.0
        else:
            turn = float(data[10])
        if data[12] == '':
            pct_chg = 0.0
        else:
            pct_chg = float(data[12])
        if data[13] == '':
            peTTM = 0.0
        else:
            peTTM = float(data[13])
        if data[14] == '':
            psTTM = 0.0
        else:
            psTTM = float(data[14])
        if data[15] == '':
            pcf_ncfTTM = 0.0
        else:
            pcf_ncfTTM = float(data[15])
        if data[16] == '':
            pbMRQ = 0.0
        else:
            pbMRQ = float(data[16])
        record = {
            'date': datetime.datetime.strptime(data[0], '%Y-%m-%d'),
            'code': data[1],
            'open': _open,
            'high': high,
            'low': low,
            'close': close,
            'pre_close': pre_close,
            'volume': volume,
            'amount': amount,
            'adjust_flag': int(data[9]),
            'turn': turn,
            'trade_status': int(data[11]),
            'pct_chg': pct_chg,
            'peTTM': peTTM,
            'psTTM': psTTM,
            'pcf_ncfTTM': pcf_ncfTTM,
            'pbMRQ': pbMRQ,
            'is_st': int(data[17])
        }
        records.append(record)
    query = AStockDayLine.insert_many(records)
    query.execute()


class FetchDayK(QThread):
    progress_signal = Signal(int)
    err_signal = Signal(str)

    def __init__(self, s_date, e_date, parent=None):
        super(FetchDayK, self).__init__(parent)
        self.s_date = s_date
        self.e_date = e_date

    def run(self):
        bs_log = bs.login()
        if bs_log.error_code != '0' or bs_log.error_msg != 'success':
            self.err_signal.emit(bs_log.error_msg)
            return False

        ret, date = fetch_last_trading_day(date=self.e_date)
        if ret != 0:
            self.err_signal.emit(date)
            return False
        ret, stock_code_list = fetch_all_code(date)
        if ret != 0:
            self.err_signal.emit(stock_code_list)
            return False
        stock_num = len(stock_code_list)
        total_num = int(stock_num / 100 * 110)
        step = int(total_num / 100)
        i = 0
        j = 0
        reset_stock_info()
        for code_info in stock_code_list:
            code = code_info[0]
            i += 1
            ret, stock_info = fetch_stock_info(code)
            if ret != 0:
                self.err_signal.emit(stock_info)
                return False
            ret, data = fetch_day_line_data(code, self.s_date, self.e_date)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            # store_stock_info()---start
            records = []
            if not stock_info:
                ipo_date = None
                out_date = None
                _type = None
                status = None
            else:
                ipo_date = datetime.datetime.strptime(stock_info[2], '%Y-%m-%d')
                if stock_info[3] != '':
                    out_date = datetime.datetime.strptime(stock_info[3],
                                                          '%Y-%m-%d')
                else:
                    out_date = None
                _type = int(stock_info[4])
                status = int(stock_info[5])
            record = {
                'code': code_info[0],
                'name': code_info[2],
                'trade_status': int(code_info[1]),
                'ipo_date': ipo_date,
                'out_date': out_date,
                'type': _type,
                'status': status
            }
            records.append(record)
            query = AStockInfo.insert_many(records)
            query.execute()
            # store_stock_info()---end
            store_day_line_data(data)
            if i % step == 0:
                j += 1
                self.progress_signal.emit(j)
        save_last_updated_date(self.e_date)
        self.progress_signal.emit(100)
        bs.logout()
        return True


if __name__ == '__main__':
    lg = bs.login()
    if lg.error_code != '0' or lg.error_msg != 'success':
        print(lg.error_code, lg.error_msg)

    # s_code = 'sh.601519'
    s_date = '2020-07-01'
    e_date = '2020-07-05'
    # # reset_k_line_data()
    # ret, k_data = _fetch_day_line_data(s_code, s_date, e_date)
    # store_day_line_data(k_data)
    #
    # s_date = '2020-06-20'
    # e_date = '2020-07-07'
    # ret, k_data = fetch_day_line_data(s_code, s_date, e_date)
    #
    # store_day_line_data(k_data)

    fdk = FetchDayK(s_date, e_date)
    fdk.run()

    # fetch_last_trading_day()
    # fetch_last_trading_day(date=e_date)

    bs.logout()
