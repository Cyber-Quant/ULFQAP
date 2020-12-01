from db.models import AStockDayLine
from apis.k_charts import fetch_sina_minute_k, fetch_tencent_k
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
    elif period == '1' or period == 'w' or period == 'm':
        data = fetch_tencent_k(code, period)
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
