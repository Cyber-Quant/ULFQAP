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

    class Meta:
        db_table = 'a_stock_info'


class AStockDayLine(BaseModel):
    id = BigAutoField()
    date = DateTimeField()
    code = CharField(index=True)
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
        indexes = (
            (('code', 'date'), False),
        )


idx = AStockDayLine.index(AStockDayLine.date.desc())
AStockDayLine.add_index(idx)


class AStockProfitData(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    pub_date = DateTimeField()
    stat_date = DateTimeField()
    ROE_avg = FloatField()
    np_margin = FloatField()
    gp_margin = FloatField()
    net_profit = FloatField()
    eps_TTM = FloatField()
    MB_revenue = FloatField()
    total_share = FloatField()
    liqa_share = FloatField()

    class Meta:
        db_table = 'a_stock_profit_data'
        indexes = (
            (('code', 'stat_date'), False),
        )


idx = AStockProfitData.index(AStockProfitData.stat_date.desc())
AStockProfitData.add_index(idx)


class AStockOperationData(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    pub_date = DateTimeField()
    stat_date = DateTimeField()
    NR_turn_ratio = FloatField()
    NR_turn_days = FloatField()
    INV_turn_ratio = FloatField()
    INV_turn_days = FloatField()
    CA_turn_ratio = FloatField()
    asset_turn_ratio = FloatField()

    class Meta:
        db_table = 'a_stock_operation_data'
        indexes = (
            (('code', 'stat_date'), False),
        )


idx = AStockOperationData.index(AStockOperationData.stat_date.desc())
AStockOperationData.add_index(idx)


class AStockGrowthData(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    pub_date = DateTimeField()
    stat_date = DateTimeField()
    YOY_equity = FloatField()
    YOY_asset = FloatField()
    YOYNI = FloatField()
    YOYPNI = FloatField()

    class Meta:
        db_table = 'a_stock_growth_data'
        indexes = (
            (('code', 'stat_date'), False),
        )


idx = AStockGrowthData.index(AStockGrowthData.stat_date.desc())
AStockGrowthData.add_index(idx)


class AStockBalanceData(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    pub_date = DateTimeField()
    stat_date = DateTimeField()
    current_ratio = FloatField()
    quick_ratio = FloatField()
    cash_ratio = FloatField()
    YOY_liability = FloatField()
    liability_to_asset = FloatField()
    asset_to_equity = FloatField()

    class Meta:
        db_table = 'a_stock_balance_data'
        indexes = (
            (('code', 'stat_date'), False),
        )


idx = AStockBalanceData.index(AStockBalanceData.stat_date.desc())
AStockBalanceData.add_index(idx)


class AStockCashFlowData(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    pub_date = DateTimeField()
    stat_date = DateTimeField()
    CA_to_asset = FloatField()
    NCA_to_asset = FloatField()
    tangible_asset_to_asset = FloatField()
    ebit_to_interest = FloatField()
    CFO_to_OR = FloatField()
    CFO_to_NP = FloatField()
    CFO_to_gr = FloatField()

    class Meta:
        db_table = 'a_stock_cash_flow_data'
        indexes = (
            (('code', 'stat_date'), False),
        )


idx = AStockCashFlowData.index(AStockCashFlowData.stat_date.desc())
AStockCashFlowData.add_index(idx)


class AStockDupontData(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    pub_date = DateTimeField()
    stat_date = DateTimeField()
    dupont_ROE = FloatField()
    dupont_asset_sto_equity = FloatField()
    dupont_asset_turn = FloatField()
    dupont_pnitoni = FloatField()
    dupont_nitogr = FloatField()
    dupont_tax_burden = FloatField()
    dupont_intburden = FloatField()
    dupont_ebittogr = FloatField()

    class Meta:
        db_table = 'a_stock_dupont_data'
        indexes = (
            (('code', 'stat_date'), False),
        )


idx = AStockDupontData.index(AStockDupontData.stat_date.desc())
AStockDupontData.add_index(idx)


class AStockPerformanceExpressReport(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    performance_exp_pub_date = DateTimeField()
    performance_exp_stat_date = DateTimeField()
    performance_exp_update_date = DateTimeField()
    performance_express_total_asset = FloatField()
    performance_express_net_asset = FloatField()
    performance_express_EPS_chg_pct = FloatField()
    performance_express_ROE_wa = FloatField()
    performance_express_EPS_diluted = FloatField()
    performance_express_GRYOY = FloatField()
    performance_express_OPYOY = FloatField()

    class Meta:
        db_table = 'a_stock_performance_express_report'
        indexes = (
            (('code', 'performance_exp_stat_date'), False),
        )


idx = AStockPerformanceExpressReport.index(
    AStockPerformanceExpressReport.performance_exp_stat_date.desc())
AStockPerformanceExpressReport.add_index(idx)


class AStockForcastReport(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    profit_forcast_exp_pub_date = DateTimeField()
    profit_forcast_exp_stat_date = DateTimeField()
    profit_forcast_type = CharField()
    profit_forcast_abstract = CharField()
    profit_forcast_chg_pct_up = FloatField()
    profit_forcast_chg_pct_down = FloatField()

    class Meta:
        db_table = 'a_stock_forcast_report'
        indexes = (
            (('code', 'profit_forcast_exp_stat_date'), False),
        )


idx = AStockForcastReport.index(
    AStockForcastReport.profit_forcast_exp_stat_date.desc())
AStockForcastReport.add_index(idx)
