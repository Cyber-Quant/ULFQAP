from peewee import *

from db.db import db


class BaseModel(Model):
    class Meta:
        database = db


class AStockInfo(BaseModel):
    id = BigAutoField()
    code = CharField(unique=True)
    name = CharField()
    trade_status = IntegerField(null=True)
    ipo_date = DateTimeField(null=True)
    out_date = DateTimeField(null=True)
    type = IntegerField(null=True)
    status = IntegerField(null=True)

    class Meta:
        db_table = 'a_stock_info'


class AStockDayLine(BaseModel):
    id = BigAutoField()
    date = DateTimeField()
    code = CharField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    pre_close = FloatField()
    volume = IntegerField()
    amount = FloatField()
    adjust_flag = IntegerField()
    turn = FloatField()
    trade_status = IntegerField()
    pct_chg = FloatField()
    peTTM = FloatField()
    psTTM = FloatField()
    pcf_ncfTTM = FloatField()
    pbMRQ = FloatField()
    is_st = IntegerField()

    class Meta:
        db_table = 'a_stock_day_line'
