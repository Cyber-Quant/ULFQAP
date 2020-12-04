import calendar
import datetime
import numpy as np

from db.models import AStockDayLine
from apis.k_charts import fetch_sina_minute_k, fetch_tencent_1_minute_k
from conf.conf import DEFAULT_K_LIMIT


def get_latest_batch_data(code, limit=DEFAULT_K_LIMIT, period='d',
                          s_date=None, e_date=None):
    date = []
    _open = []
    close = []
    high = []
    low = []
    volume = []
    ma_price = []
    ma_volume = []
    if period == 'd':
        if s_date is not None and e_date is not None:
            rows = AStockDayLine.select().where(
                AStockDayLine.code == code,
                AStockDayLine.date >= s_date,
                AStockDayLine.date <= e_date).order_by(
                AStockDayLine.date.desc())
        else:
            rows = AStockDayLine.select().where(
                AStockDayLine.code == code).order_by(
                AStockDayLine.date.desc()).limit(limit)
        for row in rows[::-1]:
            date.append(row.date.strftime('%Y-%m-%d'))
            _open.append(row.open)
            close.append(row.close)
            high.append(row.high)
            low.append(row.low)
            volume.append(row.volume)
            ma_price.append(0)
            ma_volume.append(0)
    elif period == 'w':
        monday, sunday = get_current_week_date()
        for i in reversed(range(limit)):
            s_date = monday - datetime.timedelta(days=7 * i)
            e_date = sunday - datetime.timedelta(days=7 * i)
            rows = AStockDayLine.select().where(
                AStockDayLine.code == code,
                AStockDayLine.date >= s_date,
                AStockDayLine.date <= e_date).order_by(
                AStockDayLine.date.asc())
            if rows.count() == 0:
                continue
            prices = []
            vol = 0
            for row in rows:
                prices.append(row.open)
                prices.append(row.close)
                prices.append(row.high)
                prices.append(row.low)
                vol += row.volume
            date.append(rows[-1].date.strftime('%Y-%m-%d'))
            _open.append(rows[0].open)
            close.append(rows[-1].close)
            high.append(max(prices))
            low.append(min(prices))
            volume.append(vol)
            ma_price.append(0)
            ma_volume.append(0)
    elif period == 'm':
        month_ranges = get_month_range()
        for month_range in month_ranges:
            s_date = month_range['s_date']
            e_date = month_range['e_date']
            rows = AStockDayLine.select().where(
                AStockDayLine.code == code,
                AStockDayLine.date >= s_date,
                AStockDayLine.date <= e_date).order_by(
                AStockDayLine.date.asc())
            if rows.count() == 0:
                continue
            prices = []
            vol = 0
            for row in rows:
                prices.append(row.open)
                prices.append(row.close)
                prices.append(row.high)
                prices.append(row.low)
                vol += row.volume
            date.append(rows[-1].date.strftime('%Y-%m-%d'))
            _open.append(rows[0].open)
            close.append(rows[-1].close)
            high.append(max(prices))
            low.append(min(prices))
            volume.append(vol)
            ma_price.append(0)
            ma_volume.append(0)
    elif period == '1':
        data = fetch_tencent_1_minute_k(code)
        for item in data:
            date.append(item['date'])
            _open.append(item['open'])
            close.append(item['close'])
            high.append(item['high'])
            low.append(item['low'])
            volume.append(item['volume'])
            ma_price.append(0)
            ma_volume.append(0)
    elif period == '5' or period == '15' or period == '30' or period == '60':
        data = fetch_sina_minute_k(code, period)
        for item in data:
            date.append(item['date'])
            _open.append(item['open'])
            close.append(item['close'])
            high.append(item['high'])
            low.append(item['low'])
            volume.append(item['volume'])
            if period != '60':
                _ma_price = float(item['ma_price'])
                _ma_volume = int(item['ma_volume'])
            else:
                _ma_price = 0
                _ma_volume = 0
            ma_price.append(_ma_price)
            ma_volume.append(_ma_volume)
    return date, _open, close, high, low, volume, ma_price, ma_volume


def get_current_week_date():
    monday = datetime.datetime.today() - datetime.timedelta(
        days=datetime.datetime.today().weekday())
    sunday = datetime.datetime.today() + datetime.timedelta(
        days=6 - datetime.datetime.today().weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = sunday.replace(hour=0, minute=0, second=0, microsecond=0)
    return monday, sunday


def get_current_month_beginning():
    today = datetime.datetime.today()
    month_beginning = today.replace(day=1, hour=0, minute=0, second=0,
                                    microsecond=0)
    return month_beginning


def get_month_range():
    month_beginning = get_current_month_beginning()
    year = month_beginning.year
    month = month_beginning.month
    begin, end = calendar.monthrange(year, month)
    month_ending = datetime.datetime(year=year, month=month, day=end)
    month_range = [{'s_date': month_beginning, 'e_date': month_ending}]
    for i in range(DEFAULT_K_LIMIT - 1):
        month_ending = month_beginning + datetime.timedelta(days=-1)
        month_beginning = month_ending.replace(day=1)
        month_range.append({'s_date': month_beginning, 'e_date': month_ending})
    return month_range[::-1]


def calc_wpct(buy_prices, sell_prices):
    count = len(buy_prices)
    if count == 0:
        return 0.0
    winning_count = 0
    for i in range(count):
        if buy_prices[i] < sell_prices[i]:
            winning_count += 1
    wpct = winning_count / count * 100
    return wpct


def calc_batch_ma(close, period):
    mas = []
    for i in range(len(close)):
        if i < period - 1:
            continue
        ma = np.mean(close[i - period + 1: i + 1])
        mas.append(ma)
    return mas


def calc_batch_ema(data, period):
    emas = data.copy()
    for i in range(len(data)):
        if i == 0:
            emas[i] = data[i]
        if i > 0:
            emas[i] = ((period - 1) * emas[i - 1] + 2 * data[i]) / (
                    period + 1)
    return emas
