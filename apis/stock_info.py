import baostock as bs
import datetime
import json

from conf.conf import global_config_path, DAY_K_READY_HOUR, DAY_K_READY_MINUTE
from db.models import AStockInfo
from db.ops import create_table, drop_table


def save_last_updated_date(new_trading_day, flag):
    key = 'index_update_date'
    if flag == 'i':
        key = 'index_update_date'
    elif flag == 'd':
        key = 'day_k_update_date'
    if not global_config_path.exists():
        data = {key: new_trading_day}
    else:
        with open(global_config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if key in data:
                saved_date = data[key]
            else:
                saved_date = '1970-01-01'
            new_date = datetime.datetime.strptime(new_trading_day, '%Y-%m-%d')
            old_date = datetime.datetime.strptime(saved_date, '%Y-%m-%d')
            if new_trading_day == '1970-01-01':
                data[key] = '1970-01-01'
            elif old_date >= new_date:
                data[key] = saved_date
            else:
                data[key] = new_trading_day

    with open(global_config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def reset_last_updated_date():
    date = '1970-01-01'
    save_last_updated_date(date, 'i')
    save_last_updated_date(date, 'd')


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

    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    ready_time = datetime.datetime(year, month, day, DAY_K_READY_HOUR,
                                   DAY_K_READY_MINUTE, 0, 0)
    if now >= ready_time:
        return 0, trading_days[-1]
    else:
        return 0, trading_days[-2]


def get_last_updated_date(flag):
    key = 'index_update_date'
    if flag == 'i':
        key = 'index_update_date'
    elif flag == 'd':
        key = 'day_k_update_date'

    if not global_config_path.exists():
        return '1970-01-01'
    else:
        with open(global_config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if key in data:
                stored_date = data[key]
            else:
                stored_date = '1970-01-01'
        return stored_date


def need_update(flag):
    lg = bs.login()
    if lg.error_code != '0' or lg.error_msg != 'success':
        return lg.error_msg

    ret, new_trading_day = fetch_last_trading_day()
    if ret != 0:
        return new_trading_day

    bs.logout()

    stored_date = get_last_updated_date(flag)
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
