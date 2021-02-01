import baostock as bs
import datetime
import json
import requests

from qtpy.QtCore import *

from apis.stock_info import fetch_all_code, reset_stock_info, \
    fetch_last_trading_day, fetch_stock_info
from conf.conf import DEFAULT_K_LIMIT, FIRST_DAY
from db.models import AStockInfo, AStockDayLine
from db.ops import create_table, drop_table


def reset_k_line_data():
    drop_table(AStockDayLine)
    create_table(AStockDayLine)


def _fetch_day_line_data(code, start_date, end_date):
    fields = 'date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST'
    frequency = 'd'
    rs = bs.query_history_k_data_plus(code,
                                      fields,
                                      start_date=start_date,
                                      end_date=end_date,
                                      frequency=frequency, adjustflag='3')
    if rs.error_code != '0' or rs.error_msg != 'success':
        return int(rs.error_code), rs.error_msg

    data_list = []
    while (rs.error_code == '0') & rs.next():
        data = rs.get_row_data()
        if len(data) > 0:
            data_list.append(data)

    return 0, data_list


def fetch_day_line_data(code, end_date):
    charts = AStockDayLine.select().where(AStockDayLine.code == code).order_by(
        AStockDayLine.date.desc())
    if charts.count() == 0:
        day_ret, day_data = _fetch_day_line_data(code, FIRST_DAY, end_date)
        if day_ret != 0:
            return -1, day_data
        else:
            return 0, day_data

    day_data_list = []
    if datetime.datetime.strptime(end_date, '%Y-%m-%d') > charts[0].date:
        new_start_date = charts[0].date + datetime.timedelta(1)
        new_start_date_str = new_start_date.strftime('%Y-%m-%d')
        day_ret, day_newer_data = _fetch_day_line_data(code, new_start_date_str,
                                                       end_date)
        if day_ret != 0:
            return -1, day_newer_data
        day_data_list = day_data_list + day_newer_data
    return 0, day_data_list


def store_day_line_data(day_data_list):
    day_records = []
    for day_data in day_data_list:
        if day_data[2] == '':
            _open = 0.0
        else:
            _open = float(day_data[2])
        if day_data[3] == '':
            high = 0.0
        else:
            high = float(day_data[3])
        if day_data[4] == '':
            low = 0.0
        else:
            low = float(day_data[4])
        if day_data[5] == '':
            close = 0.0
        else:
            close = float(day_data[5])
        if day_data[6] == '':
            pre_close = 0.0
        else:
            pre_close = float(day_data[6])
        if day_data[7] == '':
            volume = 0
        else:
            volume = int(day_data[7])
        if day_data[8] == '':
            amount = 0.0
        else:
            amount = float(day_data[8])
        if day_data[10] == '':
            turn = 0.0
        else:
            turn = float(day_data[10])
        if day_data[12] == '':
            pct_chg = 0.0
        else:
            pct_chg = float(day_data[12])
        if day_data[13] == '':
            peTTM = 0.0
        else:
            peTTM = float(day_data[13])
        if day_data[14] == '':
            psTTM = 0.0
        else:
            psTTM = float(day_data[14])
        if day_data[15] == '':
            pcf_ncfTTM = 0.0
        else:
            pcf_ncfTTM = float(day_data[15])
        if day_data[16] == '':
            pbMRQ = 0.0
        else:
            pbMRQ = float(day_data[16])
        if day_data[17] == '':
            is_st = 0
        else:
            is_st = int(day_data[17])
        record = {
            'date': datetime.datetime.strptime(day_data[0], '%Y-%m-%d'),
            'code': day_data[1],
            'open': _open,
            'high': high,
            'low': low,
            'close': close,
            'pre_close': pre_close,
            'volume': volume,
            'amount': amount,
            'adjust_flag': int(day_data[9]),
            'turn': turn,
            'trade_status': int(day_data[11]),
            'pct_chg': pct_chg,
            'peTTM': peTTM,
            'psTTM': psTTM,
            'pcf_ncfTTM': pcf_ncfTTM,
            'pbMRQ': pbMRQ,
            'is_st': is_st
        }
        day_records.append(record)

    day_query = AStockDayLine.insert_many(day_records)
    day_query.execute()


def get_code_list():
    rows = AStockInfo.select()
    code_list = []
    for row in rows:
        code_list.append(row.code)
    return code_list


class UpdateStockInfo(QThread):
    sig_up_stock_info = Signal(int)
    sig_up_stock_info_done = Signal()
    err_signal = Signal(str)

    def __init__(self, date, parent=None):
        super(UpdateStockInfo, self).__init__(parent)
        self.date = date

    def run(self):
        lg = bs.login()
        if lg.error_code != '0' or lg.error_msg != 'success':
            return lg.error_msg

        self.sig_up_stock_info.emit(1)
        ret, date = fetch_last_trading_day(date=self.date)
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
        records = []
        for code_info in stock_code_list:
            code = code_info[0]
            i += 1
            ret, stock_info = fetch_stock_info(code)
            if ret != 0:
                self.err_signal.emit(stock_info)
                return False
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
            if i % step == 0:
                j += 1
                self.sig_up_stock_info.emit(j)
        query = AStockInfo.insert_many(records)
        query.execute()
        self.sig_up_stock_info_done.emit()
        bs.logout()
        return True


class FetchDayK(QThread):
    sig_fetch_day_k = Signal(int)
    sig_fetch_day_k_done = Signal()
    err_signal = Signal(str)

    def __init__(self, e_date, code_list, parent=None):
        super(FetchDayK, self).__init__(parent)
        self.e_date = e_date
        self.stock_code_list = code_list

    def run(self):
        lg = bs.login()
        if lg.error_code != '0' or lg.error_msg != 'success':
            return lg.error_msg

        self.sig_fetch_day_k.emit(1)
        stock_num = len(self.stock_code_list)
        total_num = int(stock_num / 100 * 110)
        step = int(total_num / 100)
        i = 0
        j = 0
        for code in self.stock_code_list:
            i += 1
            ret, data = fetch_day_line_data(code, self.e_date)
            if ret != 0:
                self.err_signal.emit(data)
                return False
            store_day_line_data(data)
            if i % step == 0:
                j += 1
                self.sig_fetch_day_k.emit(j)
        self.sig_fetch_day_k_done.emit()
        bs.logout()
        return True


def fetch_sina_minute_k(code, period):
    code = code.replace('.', '')
    url = 'http://money.finance.sina.com.cn/quotes_service/api/' \
          'json_v2.php/CN_MarketData.getKLineData?symbol='
    url = url + code + '&scale=' + period + '&ma=' + period + '&datalen=' + str(
        DEFAULT_K_LIMIT)
    res = requests.get(url).text
    items = json.loads(res)
    k_charts = []
    for item in items:
        k_chart = {
            'date': item['day'],
            'open': float(item['open']),
            'close': float(item['close']),
            'high': float(item['high']),
            'low': float(item['low']),
            'volume': int(item['volume']),
        }
        if period != '60':
            k_chart['ma_price'] = float(item['ma_price' + period])
            k_chart['ma_volume'] = int(item['ma_volume' + period])

        k_charts.append(k_chart)
    return k_charts


def fetch_tencent_1_minute_k(code):
    code = code.replace('.', '') + '.js'
    base = 'http://data.gtimg.cn/flashdata/hushen/minute/'
    url = base + code
    res = requests.get(url).text
    res_list = res.split('\\n\\\n')
    k_charts = []
    for item in res_list[2:-1]:
        item_list = item.split(' ')
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        _date = datetime.datetime(year, month, day,
                                  int(item_list[0][:2], 10),
                                  int(item_list[0][2:], 10),
                                  0, 0)
        data_str = _date.strftime('%Y-%m-%d %H:%M:%S')
        date = data_str
        _open = float(item_list[1])
        close = float(item_list[1])
        high = float(item_list[1])
        low = float(item_list[1])
        vol = int(item_list[2])
        k_chart = {
            'date': date,
            'open': _open,
            'close': close,
            'high': high,
            'low': low,
            'volume': vol,
        }
        k_charts.append(k_chart)
    return k_charts


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
