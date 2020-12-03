import baostock as bs
import datetime
import json

from pathlib import Path

from apis.stock_info import fetch_last_trading_day, fetch_all_code
from apis.k_charts import fetch_day_line_data, store_day_line_data


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
            print('下载', code, '时出错，退出，接着跑')
            break
        store_day_line_data(data)

    bs.logout()


if __name__ == '__main__':
    codes = get_codes()
    download_data(codes)
