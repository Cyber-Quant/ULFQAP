import baostock as bs
import datetime
import json
import time

from conf.conf import global_config_path
from db.models import AStockInfo
from db.ops import create_table, drop_table


def save_last_updated_date(new_trading_day):
    if not global_config_path.exists():
        data = {'date': new_trading_day}
    else:
        with open(global_config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'date' in data:
                saved_date = data['date']
            else:
                saved_date = '1970-01-01'
            new_date = datetime.datetime.strptime(new_trading_day, '%Y-%m-%d')
            old_date = datetime.datetime.strptime(saved_date, '%Y-%m-%d')
            if new_trading_day == '1970-01-01':
                data['date'] = '1970-01-01'
            elif old_date >= new_date:
                data['date'] = saved_date
            else:
                data['date'] = new_trading_day

    with open(global_config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def reset_last_updated_date():
    date = '1970-01-01'
    save_last_updated_date(date)


def reset_stock_info():
    drop_table(AStockInfo)
    create_table(AStockInfo)


def fetch_last_trading_day(date=None):
    now_time = datetime.datetime.now()
    if date is not None:
        now_time = datetime.datetime.strptime(date, '%Y-%m-%d')
    # In past 20 days, it must have some trade days.
    start_time = now_time + datetime.timedelta(days=-20)
    start_date = start_time.strftime('%Y-%m-%d')

    rs = bs.query_trade_dates(start_date=start_date)
    if rs.error_code != '0' or rs.error_msg != 'success':
        return int(rs.error_code), rs.error_msg
    date_list = []
    while (rs.error_code == '0') & rs.next():
        date_list.append(rs.get_row_data())

    trading_days = []
    for day in date_list:
        if day[1] == '1':
            trading_days.append(day[0])
    now = time.localtime()
    from conf.conf import DAY_K_READY_HOUR, DAY_K_READY_MINUTE
    if now.tm_hour >= DAY_K_READY_HOUR and now.tm_min > DAY_K_READY_MINUTE:
        return 0, trading_days[-1]
    else:
        return 0, trading_days[-2]


def get_last_updated_date():
    if not global_config_path.exists():
        return '1970-01-01'
    else:
        with open(global_config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'date' in data:
                stored_date = data['date']
            else:
                stored_date = '1970-01-01'
        return stored_date


def need_update():
    lg = bs.login()
    if lg.error_code != '0' or lg.error_msg != 'success':
        return lg.error_msg

    ret, new_trading_day = fetch_last_trading_day()
    if ret != 0:
        return new_trading_day

    bs.logout()

    stored_date = get_last_updated_date()
    new_date = datetime.datetime.strptime(new_trading_day, '%Y-%m-%d')
    old_date = datetime.datetime.strptime(stored_date, '%Y-%m-%d')
    if old_date >= new_date:
        return -1
    else:
        return 0


def fetch_all_code(trading_day):
    rs = bs.query_all_stock(day=trading_day)
    if rs.error_code != '0' or rs.error_msg != 'success':
        return int(rs.error_code), rs.error_msg

    stock_code_list = []
    while (rs.error_code == '0') & rs.next():
        data = rs.get_row_data()
        stock_code_list.append(data)
    return 0, stock_code_list


def fetch_stock_info(code):
    rs = bs.query_stock_basic(code=code)
    if rs.error_code != '0' or rs.error_msg != 'success':
        return int(rs.error_code), rs.error_msg
    return 0, rs.get_row_data()


if __name__ == '__main__':
    ret = need_update()
    print(ret)
