import baostock as bs
import datetime

from apis.code_index import fetch_last_trading_day, fetch_all_code, \
    store_all_code
from apis.k_charts import fetch_day_line_data, store_day_line_data, \
    get_code_list


# TODO: Due to the '_MEIPASS' attr, I don't know how to make it runnable
#  under its current directory.  I have to put this script into the ROOT
#  directory to run it.

def download_index():
    lg = bs.login()

    ret, date = fetch_last_trading_day()
    ret, data = fetch_all_code(date)
    store_all_code(data)

    bs.logout()


def get_codes():
    codes = get_code_list()
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

    bs.logout()


if __name__ == '__main__':
    download_index()
    codes = get_codes()
    download_data(codes)
