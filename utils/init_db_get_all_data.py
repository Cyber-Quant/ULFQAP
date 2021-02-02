import baostock as bs
import datetime

from apis.code_index import fetch_last_trading_day, fetch_all_code, \
    store_all_code
from apis.finance import fetch_balance_data, fetch_cash_flow_data, \
    fetch_dupont_data, fetch_growth_data, fetch_operation_data, \
    fetch_profit_data, store_balance_data, store_cash_flow_data, \
    store_dupont_data, store_growth_data, store_operation_data, \
    store_profit_data
from apis.k_charts import fetch_day_line_data, store_day_line_data, \
    get_code_list
from apis.statements import fetch_performance_express_report, \
    fetch_forecast_report, store_performance_express_report, \
    store_forecast_report


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

        ret, data = fetch_performance_express_report(code, today)
        if ret != 0:
            print('下载', code, '业绩快报时出错，退出，接着跑')
            break
        store_performance_express_report(data)

        ret, data = fetch_forecast_report(code, today)
        if ret != 0:
            print('下载', code, '业绩预告时出错，退出，接着跑')
            break
        store_forecast_report(data)

    bs.logout()


if __name__ == '__main__':
    download_index()
    codes = get_codes()
    download_data(codes)
