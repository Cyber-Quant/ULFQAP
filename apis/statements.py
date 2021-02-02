import baostock as bs
import datetime

from qtpy.QtCore import *

from conf.conf import FIRST_DAY
from db.models import AStockPerformanceExpressReport, AStockForcastReport
from db.ops import create_table, drop_table


def reset_statements_data():
    drop_table(AStockPerformanceExpressReport)
    create_table(AStockPerformanceExpressReport)
    drop_table(AStockForcastReport)
    create_table(AStockForcastReport)


def _fetch_performance_express_report(code, start_date, end_date):
    data_list = []
    rs = bs.query_performance_express_report(code,
                                             start_date=start_date,
                                             end_date=end_date)
    if rs.error_code != '0' or rs.error_msg != 'success':
        return int(rs.error_code), rs.error_msg
    while (rs.error_code == '0') & rs.next():
        data = rs.get_row_data()
        if len(data) > 0:
            data_list.append(data)
    return 0, data_list


def fetch_performance_express_report(code, end_date):
    rows = AStockPerformanceExpressReport.select().where(
        AStockPerformanceExpressReport.code ==
        code).order_by(
        AStockPerformanceExpressReport.performance_exp_stat_date.desc())

    if rows.count() == 0:
        ret, data = _fetch_performance_express_report(code, FIRST_DAY,
                                                      end_date)
        if ret != 0:
            return -1, data
        else:
            return 0, data

    data = []
    if datetime.datetime.strptime(end_date, '%Y-%m-%d') > \
            rows[0].performance_exp_stat_date:
        new_start_date = \
            rows[0].performance_exp_stat_date + datetime.timedelta(1)
        new_start_date_str = new_start_date.strftime('%Y-%m-%d')
        ret, newer_data = \
            _fetch_performance_express_report(code, new_start_date_str,
                                              end_date)
        if ret != 0:
            return -1, newer_data
        data = data + newer_data
    return 0, data


def store_performance_express_report(data_list):
    records = []
    for data in data_list:
        if data[4] == '':
            performance_express_total_asset = 0.0
        else:
            performance_express_total_asset = float(data[4])
        if data[5] == '':
            performance_express_net_asset = 0.0
        else:
            performance_express_net_asset = float(data[5])
        if data[6] == '':
            performance_express_EPS_chg_pct = 0.0
        else:
            performance_express_EPS_chg_pct = float(data[6])
        if data[7] == '':
            performance_express_ROE_wa = 0.0
        else:
            performance_express_ROE_wa = float(data[7])
        if data[8] == '':
            performance_express_EPS_diluted = 0.0
        else:
            performance_express_EPS_diluted = float(data[8])
        if data[9] == '':
            performance_express_GRYOY = 0.0
        else:
            performance_express_GRYOY = float(data[9])
        if data[10] == '':
            performance_express_OPYOY = 0.0
        else:
            performance_express_OPYOY = float(data[10])
        record = {
            'code': data[0],
            'performance_exp_pub_date': datetime.datetime.strptime(data[1],
                                                                   '%Y-%m-%d'),
            'performance_exp_stat_date': datetime.datetime.strptime(data[2],
                                                                    '%Y-%m-%d'),
            'performance_exp_update_date': datetime.datetime.strptime(data[3],
                                                                      '%Y-%m-%d'),
            'performance_express_total_asset': performance_express_total_asset,
            'performance_express_net_asset': performance_express_net_asset,
            'performance_express_EPS_chg_pct': performance_express_EPS_chg_pct,
            'performance_express_ROE_wa': performance_express_ROE_wa,
            'performance_express_EPS_diluted': performance_express_EPS_diluted,
            'performance_express_GRYOY': performance_express_GRYOY,
            'performance_express_OPYOY': performance_express_OPYOY
        }
        records.append(record)
    query = AStockPerformanceExpressReport.insert_many(records)
    query.execute()


def _fetch_forecast_report(code, start_date, end_date):
    data_list = []
    rs = bs.query_forecast_report(code,
                                  start_date=start_date,
                                  end_date=end_date)
    if rs.error_code != '0' or rs.error_msg != 'success':
        return int(rs.error_code), rs.error_msg
    while (rs.error_code == '0') & rs.next():
        data = rs.get_row_data()
        if len(data) > 0:
            data_list.append(data)
    return 0, data_list


def fetch_forecast_report(code, end_date):
    rows = AStockForcastReport.select().where(AStockForcastReport.code ==
                                              code).order_by(
        AStockForcastReport.profit_forcast_exp_stat_date.desc())

    if rows.count() == 0:
        ret, data = _fetch_forecast_report(code, FIRST_DAY,
                                           end_date)
        if ret != 0:
            return -1, data
        else:
            return 0, data

    data = []
    if datetime.datetime.strptime(end_date, '%Y-%m-%d') > \
            rows[0].profit_forcast_exp_stat_date:
        new_start_date = \
            rows[0].profit_forcast_exp_stat_date + datetime.timedelta(1)
        new_start_date_str = new_start_date.strftime('%Y-%m-%d')
        ret, newer_data = \
            _fetch_forecast_report(code, new_start_date_str,
                                   end_date)
        if ret != 0:
            return -1, newer_data
        data = data + newer_data
    return 0, data


def store_forecast_report(data_list):
    records = []
    for data in data_list:
        if data[5] == '':
            profit_forcast_chg_pct_up = 0.0
        else:
            profit_forcast_chg_pct_up = float(data[5])
        if data[6] == '':
            profit_forcast_chg_pct_down = 0.0
        else:
            profit_forcast_chg_pct_down = float(data[6])
        record = {
            'code': data[0],
            'profit_forcast_exp_pub_date': datetime.datetime.strptime(data[1],
                                                                      '%Y-%m-%d'),
            'profit_forcast_exp_stat_date': datetime.datetime.strptime(data[2],
                                                                       '%Y-%m-%d'),
            'profit_forcast_type': data[3],
            'profit_forcast_abstract': data[4],
            'profit_forcast_chg_pct_up': profit_forcast_chg_pct_up,
            'profit_forcast_chg_pct_down': profit_forcast_chg_pct_down
        }
        records.append(record)
    query = AStockForcastReport.insert_many(records)
    query.execute()
