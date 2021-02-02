import baostock as bs
import datetime
import json

from pathlib import Path

from apis.finance import fetch_balance_data, fetch_cash_flow_data, \
    fetch_dupont_data, fetch_growth_data, fetch_operation_data, \
    fetch_profit_data, store_balance_data, store_cash_flow_data, \
    store_dupont_data, store_growth_data, store_operation_data, \
    store_profit_data
from apis.k_charts import fetch_day_line_data, store_day_line_data
from apis.stock_info import fetch_last_trading_day, fetch_all_code


# TODO: Due to the '_MEIPASS' attr, I don't know how to make it runnable
#  under its current directory.  I have to put this script into the ROOT
#  directory to run it.

def download_index():
    lg = bs.login()

    ret, date = fetch_last_trading_day()
    ret, result_list = fetch_all_code(date)
    codes = []
    stocks = []
    for item in result_list:
        codes.append(item[0])
        stocks.append({'code': item[0],
                       'name': item[2],
                       'trade_status': item[1]})
    with open('codes.json', 'w', encoding='utf-8') as f:
        json.dump(codes, f, indent=4, ensure_ascii=False)
    with open('stocks.json', 'w', encoding='utf-8') as f:
        json.dump(stocks, f, indent=4, ensure_ascii=False)
    bs.logout()


def get_codes():
    codes_path = Path('codes.json')
    if not codes_path.exists():
        download_index()
    with open(codes_path, 'r', encoding='utf-8') as f:
        codes = json.load(f)
    return codes


def download_data(codes):
    lg = bs.login()

    now = datetime.datetime.now()
    today = now.strftime('%Y-%m-%d')

    for code in codes:
        print('Downloading: ' + code)
        ret, data = fetch_day_line_data(code, today)
        if ret != 0:
            print('下载', code, 'K线时出错，退出，接着跑')
            break
        store_day_line_data(data)

        ret, data = fetch_profit_data(code)
        if ret != 0:
            print('下载', code, '盈利能力时出错，退出，接着跑')
            break
        store_profit_data(data)

        ret, data = fetch_operation_data(code)
        if ret != 0:
            print('下载', code, '运营能力时出错，退出，接着跑')
            break
        store_operation_data(data)

        ret, data = fetch_growth_data(code)
        if ret != 0:
            print('下载', code, '成长能力时出错，退出，接着跑')
            break
        store_growth_data(data)

        ret, data = fetch_balance_data(code)
        if ret != 0:
            print('下载', code, '偿债能力时出错，退出，接着跑')
            break
        store_balance_data(data)

        ret, data = fetch_cash_flow_data(code)
        if ret != 0:
            print('下载', code, '现金流时出错，退出，接着跑')
            break
        store_cash_flow_data(data)

        ret, data = fetch_dupont_data(code)
        if ret != 0:
            print('下载', code, '杜邦指数时出错，退出，接着跑')
            break
        store_dupont_data(data)

    bs.logout()


if __name__ == '__main__':
    codes = get_codes()
    download_data(codes)
