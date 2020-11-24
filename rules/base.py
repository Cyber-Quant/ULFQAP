from db.models import AStockDayLine, AStockWeekLine, AStockMonthLine


def get_latest_n_desc_data(code, limit, period='d'):
    if period == 'd':
        rows = AStockDayLine.select().where(
            AStockDayLine.code == code).order_by(
            AStockDayLine.date.desc()).limit(limit)
    elif period == 'w':
        rows = AStockWeekLine.select().where(
            AStockWeekLine.code == code).order_by(
            AStockWeekLine.date.desc()).limit(limit)
    elif period == 'm':
        rows = AStockMonthLine.select().where(
            AStockMonthLine.code == code).order_by(
            AStockMonthLine.date.desc()).limit(limit)
    return rows


def get_last_desc_data(code):
    row = AStockDayLine.select().where(
        AStockDayLine.code == code).order_by(
        AStockDayLine.date.desc()).get()
    return row
