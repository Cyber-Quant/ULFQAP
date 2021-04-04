from peewee import *

from db.db import db


class BaseModel(Model):
    class Meta:
        database = db


class AStockIndex(BaseModel):
    id = BigAutoField()
    code = CharField(unique=True)
    name = CharField()
    trade_status = IntegerField(null=True)

    class Meta:
        db_table = 'a_stock_index'


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


class AStockYJBB(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    name = CharField()
    security_type = CharField()
    trade_market = CharField()
    latest_notice_date = DateTimeField()  # 最新公告日期
    report_date = DateTimeField()
    basic_eps = FloatField()  # 每股收益(元)
    cut_basic_eps = FloatField()
    total_operate_reve = FloatField()  # 营业收入(元)
    ystz = FloatField()  # 同比增长(%)
    yshz = FloatField()  # 季环比增长(%)
    parent_net_profit = FloatField()  # 净利润
    sjltz = FloatField()  # 同比增长(%)
    sjlhz = FloatField()  # 季环比增长(%)
    roe_weighted = FloatField()  # 净资产收益率(%)
    bps = FloatField()  # 每股净资产(元)
    mgjyxjje = FloatField()  # 每股经营现金流(元)
    xsmll = FloatField()  # 销售毛利率(%)
    publish_name = CharField()  # 所处行业
    assign_dscrpt = CharField()
    gxl = FloatField()
    security_type_code = CharField()
    trade_market_code = CharField()
    first_notice_date = DateTimeField()

    class Meta:
        db_table = 'a_stock_yjbb'
        indexes = (
            (('code', 'latest_notice_date'), False),
            (('code', 'first_notice_date'), False),
        )


idx = AStockYJBB.index(AStockYJBB.latest_notice_date.desc())
AStockYJBB.add_index(idx)
idx = AStockYJBB.index(AStockYJBB.first_notice_date.desc())
AStockYJBB.add_index(idx)


class AStockYJKB(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    name = CharField()
    security_type = CharField()
    trade_market = CharField()
    ldate = DateTimeField()  # 公告日期
    rdate = DateTimeField()
    basic_eps = FloatField()  # 每股收益(元)
    yysr = FloatField()  # 营业收入(元)
    qntqys = FloatField()  # 去年同期(元)
    ys = FloatField()  # 同比增长(%)
    yshz = FloatField()  # 季环比增长(%)是通过这个算出来的，但是怎么算我不知道
    jlr = FloatField()  # 净利润
    qntqjlr = FloatField()  # 去年同期(元)
    lr = FloatField()  # 同比增长(%)
    sjlhz = FloatField()  # 季环比增长(%)是通过这个算出来的，但是怎么算我不知道
    parent_bvps = FloatField()  # 每股净资产(元)
    roe_weighted = FloatField()  # 净资产收益率(%)
    publish_name = CharField()  # 所处行业
    security_type_code = CharField()
    trade_market_code = CharField()
    first_notice_date = DateTimeField()

    class Meta:
        db_table = 'a_stock_yjkb'
        indexes = (
            (('code', 'first_notice_date'), False),
            (('code', 'ldate'), False),
        )


idx = AStockYJKB.index(AStockYJKB.ldate.desc())
AStockYJKB.add_index(idx)
idx = AStockYJKB.index(AStockYJKB.first_notice_date.desc())
AStockYJKB.add_index(idx)


class AStockYJYG(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    name = CharField()
    sclx = CharField()  # 所处板块
    end_date = DateTimeField()
    ndate = DateTimeField()  # 公告日期
    forecastl = FloatField()  # 预测数值下限(元)
    forecastt = FloatField()  # 预测数值上限(元)
    increasel = FloatField()  # 业绩变动幅度上限(%)
    increaset = FloatField()  # 业绩变动幅度下限(%)
    forecast_content = CharField()  # 业绩变动
    change_reason_descrpt = CharField()  # 业绩变动原因
    forecast_type = CharField()  # 预告类型
    year_earlier = FloatField()  # 上年同期值(元)
    hymc = CharField()  # 所处行业
    zfpx = FloatField()
    jlrpx = FloatField()
    forecast = CharField()
    is_latest = CharField()
    security_type_code = CharField()
    trade_market_code = CharField()

    class Meta:
        db_table = 'a_stock_yjyg'
        indexes = (
            (('code', 'ndate'), False),
        )


idx = AStockYJYG.index(AStockYJYG.ndate.desc())
AStockYJYG.add_index(idx)


class AStockZCFZB(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    hy_code = CharField()
    company_code = CharField()
    name = CharField()
    publish_name = CharField()  # 所处行业
    mkt = CharField()
    report_time_type_code = CharField()
    combine_type_code = CharField()
    data_ajust_type = IntegerField()
    notice_date = DateTimeField()  # 公告日期
    report_date = DateTimeField()
    sum_asset = FloatField()  # 总资产(元)
    fixed_asset = FloatField()
    monetary_fund = FloatField()  # 货币资金(元)
    monetary_fund_tb = FloatField()
    account_rec = FloatField()  # 应收帐款(元)
    account_rec_tb = FloatField()
    inventory = FloatField()  # 存货(元)
    inventory_tb = FloatField()
    tsatz = FloatField()  # 总资产同比(%)
    sum_liab = FloatField()  # 总负债
    account_pay = FloatField()  # 应付帐款(元)
    account_pay_tb = FloatField()
    advance_receive = FloatField()  # 预收帐款(元)
    advance_receive_tb = FloatField()
    sum_sh_equity_tb = FloatField()
    tdetz = FloatField()  # 总负债同比(%)
    ld = FloatField()
    zcfzl = FloatField()  # 资产负债率(%)
    cash_and_deposit_c_bank = FloatField()
    cash_and_deposit_c_bank_tb = FloatField()
    loan_advances = FloatField()
    loan_advances_tb = FloatField()
    saleable_f_asset = FloatField()
    saleable_f_asset_tb = FloatField()
    borrow_from_bank = FloatField()
    borrow_from_bank_tb = FloatField()
    accept_deposit = FloatField()
    accept_deposit_tb = FloatField()
    sell_buy_back_f_asset = FloatField()
    sell_buy_back_f_asset_tb = FloatField()
    settlement_provision = FloatField()
    settlement_provision_tb = FloatField()
    borrow_fund = FloatField()
    borrow_fund_tb = FloatField()
    agent_trade_security = FloatField()
    agent_trade_security_tb = FloatField()
    premium_rec = FloatField()
    premium_rec_tb = FloatField()
    st_borrow = FloatField()
    st_borrow_tb = FloatField()
    premium_advance = FloatField()
    premium_advance_tb = FloatField()
    eu_time = DateTimeField()

    class Meta:
        db_table = 'a_stock_zcfzb'
        indexes = (
            (('code', 'notice_date'), False),
        )


idx = AStockZCFZB.index(AStockZCFZB.notice_date.desc())
AStockZCFZB.add_index(idx)


class AStockLRB(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    hy_code = CharField()
    company_code = CharField()
    name = CharField()
    publish_name = CharField()  # 所处行业
    report_time_type_code = CharField()
    combine_type_code = CharField()
    mkt = CharField()
    notice_date = DateTimeField()  # 公告日期
    report_date = DateTimeField()
    parent_net_profit = FloatField()  # 净利润(元)
    sjlktz = FloatField()  # 净利润同比(%) x100
    total_operate_reve = FloatField()  # 营业总收入(元)
    tystz = FloatField()  # 营业总收入同比(%) x100
    operate_exp = FloatField()  # 营业支出(元)
    operate_exp_tb = FloatField()
    sale_exp = FloatField()  # 销售费用(元)
    manage_exp = FloatField()  # 管理费用(元)
    finance_exp = FloatField()  # 财务费用(元)
    total_operate_exp = FloatField()  # 营业总支出(元)
    total_operate_exp_tb = FloatField()
    operate_profit = FloatField()  # 营业利润(元)
    sum_profit = FloatField()  # 利润总额(元)
    income_tax = FloatField()
    operate_reve = FloatField()
    intn_reve = FloatField()
    intn_reve_tb = FloatField()
    commn_reve = FloatField()
    commn_reve_tb = FloatField()
    operate_tax = FloatField()
    operate_manage_exp = FloatField()
    comm_reve_comm_exp = FloatField()
    intn_reve_int_exp = FloatField()
    premium_earned = FloatField()
    premium_earned_tb = FloatField()
    invest_income = FloatField()
    invest_income_tb = FloatField()
    surrender_premium = FloatField()
    indemnity_exp = FloatField()
    yltz = FloatField()
    sjltz = FloatField()
    kcfjcxsyjlr = FloatField()
    eu_time = DateTimeField()
    yyzc = FloatField()

    class Meta:
        db_table = 'a_stock_lrb'
        indexes = (
            (('code', 'notice_date'), False),
        )


idx = AStockLRB.index(AStockLRB.notice_date.desc())
AStockLRB.add_index(idx)


class AStockXJLLB(BaseModel):
    id = BigAutoField()
    code = CharField(index=True)
    hy_code = CharField()
    company_code = CharField()
    name = CharField()
    publish_name = CharField()  # 所处行业
    report_time_type_code = CharField()
    combine_type_code = CharField()
    data_ajust_type = IntegerField()
    mkt = CharField()
    notice_date = DateTimeField()  # 公告日期
    report_date = DateTimeField()
    ni_cash_equi = FloatField()  # 净现金流(元)
    ni_cash_equi_zb = FloatField()  # 同比增长(%) x100
    net_operate_cash_flow = FloatField()  # 现金流净额(元)
    net_operate_cash_flow_zb = FloatField()  # 净现金流占比(%) x100
    net_inv_cash_flow = FloatField()  # 现金流净额(元)
    net_inv_cash_flow_zb = FloatField()  # 净现金流占比(%) x100
    net_fina_cash_flow = FloatField()  # 现金流净额(元)
    net_fina_cash_flow_zb = FloatField()  # 净现金流占比(%) x100
    sale_goods_service_rec = FloatField()
    sale_goods_service_rec_zb = FloatField()
    employee_pay = FloatField()
    employee_pay_zb = FloatField()
    inv_income_rec = FloatField()
    inv_income_rec_zb = FloatField()
    buy_fil_asset_pay = FloatField()
    buy_fil_asset_pay_zb = FloatField()
    ni_client_deposit = FloatField()
    ni_client_deposit_zb = FloatField()
    ni_loan_advances = FloatField()
    ni_loan_advances_zb = FloatField()
    intand_comm_rec = FloatField()
    intand_comm_rec_zb = FloatField()
    agent_uw_security_rec = FloatField()
    inv_pay = FloatField()
    inv_pay_zb = FloatField()
    cash_equi_beginning = FloatField()
    cash_equi_beginning_zb = FloatField()
    cash_equi_ending = FloatField()
    cash_equi_ending_zb = FloatField()
    premium_rec = FloatField()
    premium_rec_zb = FloatField()
    indemnity_pay = FloatField()
    indemnity_pay_zb = FloatField()
    eu_time = DateTimeField()
    ni_deposit = FloatField()
    ni_deposit_zb = FloatField()

    class Meta:
        db_table = 'a_stock_xjllb'
        indexes = (
            (('code', 'notice_date'), False),
        )


idx = AStockXJLLB.index(AStockXJLLB.notice_date.desc())
AStockXJLLB.add_index(idx)


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
