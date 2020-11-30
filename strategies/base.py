from db.models import AStockDayLine


def get_latest_n_desc_data(code, limit, period='d'):
    if period == 'd':
        rows = AStockDayLine.select().where(
            AStockDayLine.code == code).order_by(
            AStockDayLine.date.desc()).limit(limit)
    return rows


def get_last_desc_data(code):
    row = AStockDayLine.select().where(
        AStockDayLine.code == code).order_by(
        AStockDayLine.date.desc()).get()
    return row
