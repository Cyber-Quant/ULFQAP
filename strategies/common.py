import calendar
import datetime
import numpy as np

from db.models import AStockDayLine, AStockIndex, AStockBalanceData, \
    AStockOperationData, AStockProfitData
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
    amount = []
    turn = []
    pct_chg = []
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
            amount.append(row.amount)
            turn.append(row.turn)
            pct_chg.append(row.pct_chg)
            ma_price.append(0)
            ma_volume.append(0)
    elif period == 'w':
        monday, sunday = get_current_week_date()
        total_share = get_total_share(code)
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
            _amount = 0
            _turn = 0
            for row in rows:
                prices.append(row.open)
                prices.append(row.close)
                prices.append(row.high)
                prices.append(row.low)
                vol += row.volume
                _amount += row.amount
                _turn += row.turn
            turn_w = _turn / total_share * 100
            pct_chg_w = abs(rows[0].open - rows[-1].close) / rows[0].open * 100
            date.append(rows[-1].date.strftime('%Y-%m-%d'))
            _open.append(rows[0].open)
            close.append(rows[-1].close)
            high.append(max(prices))
            low.append(min(prices))
            volume.append(vol)
            amount.append(_amount)
            turn.append(turn_w)
            pct_chg.append(pct_chg_w)
            ma_price.append(0)
            ma_volume.append(0)
    elif period == 'm':
        month_ranges = get_month_range()
        total_share = get_total_share(code)
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
            _amount = 0
            _turn = 0
            for row in rows:
                prices.append(row.open)
                prices.append(row.close)
                prices.append(row.high)
                prices.append(row.low)
                vol += row.volume
                _amount += row.amount
                _turn += row.turn
            turn_m = _turn / total_share * 100
            pct_chg_m = abs(rows[0].open - rows[-1].close) / rows[0].open * 100
            date.append(rows[-1].date.strftime('%Y-%m-%d'))
            _open.append(rows[0].open)
            close.append(rows[-1].close)
            high.append(max(prices))
            low.append(min(prices))
            volume.append(vol)
            amount.append(_amount)
            turn.append(turn_m)
            pct_chg.append(pct_chg_m)
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
            amount.append(0)
            turn.append(0)
            pct_chg.append(0)
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
            amount.append(0)
            turn.append(0)
            pct_chg.append(0)
            if period != '60':
                _ma_price = float(item['ma_price'])
                _ma_volume = int(item['ma_volume'])
            else:
                _ma_price = 0
                _ma_volume = 0
            ma_price.append(_ma_price)
            ma_volume.append(_ma_volume)
    return date, _open, close, high, low, volume, amount, turn, pct_chg, \
           ma_price, ma_volume


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


def calc_batch_smma(close, period):
    smmas = []
    close_sum = 0
    for i in range(period):
        close_sum += close[i]
    last_smma = close_sum / period

    close_sum = 0
    for i in range(len(close)):
        if i < period:
            smmas.append(last_smma)
        close_sum += close[i]
        smma = (close_sum - last_smma + close[i]) / period
        smmas.append(smma)
        last_smma = smma
    return smmas


def calc_batch_macd(closes, fast_period, slow_period, period):
    fast_ema = calc_batch_ema(closes, fast_period)
    slow_ema = calc_batch_ema(closes, slow_period)
    dif = []
    for i, data in enumerate(fast_ema):
        dif.append(fast_ema[i] - slow_ema[i])
    dea = []
    for i, data in enumerate(dif):
        if i == 0:
            dea.append(dif[i])
        else:
            dea.append(
                (2 * dif[i] + (period - 1) * dea[i - 1]) / (period + 1)
            )
    macd = []
    for i, data in enumerate(dea):
        macd.append(2 * (dif[i] - dea[i]))
    return macd, dif, dea


def calc_batch_mav(vol, period):
    mavs = []
    for i in range(len(vol)):
        if i < period - 1:
            continue
        mav = np.mean(vol[i - period + 1: i + 1])
        mavs.append(mav)
    return mavs


def filter_roe(v, date):
    stocks = []
    rows = AStockProfitData.select().where(
        AStockProfitData.ROE_avg >= v / 100,
        AStockProfitData.stat_date == date)
    for row in rows:
        code = row.code
        stocks.append(code)
    return stocks


def filter_ltv(v, date):
    return []


def filter_ito(v, date):
    stocks = []
    rows = AStockOperationData.select().where(
        AStockOperationData.INV_turn_ratio <= v,
        AStockOperationData.stat_date == date)
    for row in rows:
        code = row.code
        stocks.append(code)
    return stocks


def filter_artr(v, date):
    stocks = []
    rows = AStockOperationData.select().where(
        AStockOperationData.NR_turn_ratio <= v,
        AStockOperationData.stat_date == date)
    for row in rows:
        code = row.code
        stocks.append(code)
    return stocks


def filter_dar(v, date):
    stocks = []
    rows = AStockBalanceData.select().where(
        AStockBalanceData.liability_to_asset <= v / 100,
        AStockBalanceData.stat_date == date)
    for row in rows:
        code = row.code
        stocks.append(code)
    return stocks


def get_value_info(code, date):
    index = AStockIndex.select().where(AStockIndex.code == code)[0]
    name = index.name
    rows = AStockProfitData.select().where(
        AStockProfitData.code == code, AStockProfitData.stat_date == date)
    if rows.count() == 0:
        roe = 0
    else:
        profit_data = rows[0]
        roe = round(profit_data.ROE_avg * 100, 2)
    ltv = 0.0
    rows = AStockOperationData.select().where(
        AStockOperationData.code == code,
        AStockOperationData.stat_date == date)
    if rows.count() == 0:
        ito = 0
        artr = 0
    else:
        operation_data = rows[0]
        ito = round(operation_data.INV_turn_ratio, 2)
        artr = round(operation_data.NR_turn_ratio, 2)
    rows = AStockBalanceData.select().where(
        AStockBalanceData.code == code, AStockBalanceData.stat_date == date)
    if rows.count() == 0:
        dar = 0
    else:
        balance_data = rows[0]
        dar = round(balance_data.liability_to_asset * 100, 2)
    return code, name, roe, ltv, ito, artr, dar


def get_stat_date():
    now = datetime.datetime.now()
    year = now.year
    quarter = int((now.month - 1) / 3) + 1
    if quarter > 2:
        quarter -= 2
    else:
        year -= 1
        quarter += 2

    if quarter == 1:
        date = datetime.datetime(year, 3, 31)
    elif quarter == 2:
        date = datetime.datetime(year, 6, 30)
    elif quarter == 3:
        date = datetime.datetime(year, 9, 30)
    elif quarter == 4:
        date = datetime.datetime(year, 12, 31)
    return date


def get_liqa_share(code):
    row = AStockProfitData.select().where(
        AStockProfitData.code == code).order_by(
        AStockProfitData.stat_date.desc())[0]
    liqa_share = row.liqa_share
    return liqa_share


def get_total_share(code):
    row = AStockProfitData.select().where(
        AStockProfitData.code == code).order_by(
        AStockProfitData.stat_date.desc())[0]
    total_share = row.total_share
    return total_share
