import datetime
import json
import re
import requests

from conf.conf import FIRST_DAY_YEAR
from db.models import AStockLRB, AStockXJLLB, AStockYJBB, AStockZCFZB
from db.ops import create_table, drop_table


def reset_statements_data():
    drop_table(AStockLRB)
    create_table(AStockLRB)
    drop_table(AStockXJLLB)
    create_table(AStockXJLLB)
    drop_table(AStockYJBB)
    create_table(AStockYJBB)
    drop_table(AStockZCFZB)
    create_table(AStockZCFZB)


def set_table():
    tables = []
    for year in range(FIRST_DAY_YEAR, 2021):
        for quarter in range(1, 5):
            month = '{:02d}'.format(quarter * 3)
            if (month == '06') or (month == '09'):
                day = 30
            else:
                day = 31
            date = '{}-{}-{}'.format(year, month, day)

            categories = ['YJBB', 'ZCFZB', 'LRB', 'XJLLB']
            for category in categories:
                if category == 'YJBB':
                    category_type = 'YJBB20_' + category
                    st = 'latestnoticedate'
                    sr = -1
                    _filter = "(securitytypecode in ('058001001'," \
                              "'058001002'))(reportdate=^%s^)" % date
                    table = {
                        'date': date,
                        'category': category,
                        'category_type': category_type,
                        'st': st,
                        'sr': sr,
                        'filter': _filter
                    }
                    tables.append(table)
                elif category == 'YJKB':
                    category_type = 'YJBB20_' + category
                    st = 'ldate'
                    sr = -1
                    _filter = "(securitytypecode in ('058001001'," \
                              "'058001002'))(rdate=^%s^)" % date
                    table = {
                        'date': date,
                        'category': category,
                        'category_type': category_type,
                        'st': st,
                        'sr': sr,
                        'filter': _filter
                    }
                    tables.append(table)
                elif category == 'YJYG':
                    category_type = 'YJBB20_' + category
                    st = 'ndate'
                    sr = -1
                    _filter = " (IsLatest='T')(enddate=^2018-06-30^)"
                    table = {
                        'date': date,
                        'category': category,
                        'category_type': category_type,
                        'st': st,
                        'sr': sr,
                        'filter': _filter
                    }
                    tables.append(table)
                elif category == 'YYPL':
                    category_type = 'YJBB20_' + category
                    st = 'frdate'
                    sr = 1
                    _filter = "(securitytypecode ='058001001')" \
                              "(reportdate=^%s^)" % date
                    table = {
                        'date': date,
                        'category': category,
                        'category_type': category_type,
                        'st': st,
                        'sr': sr,
                        'filter': _filter
                    }
                    tables.append(table)
                else:
                    category_type = 'CWBB_' + category
                    st = 'noticedate'
                    sr = -1
                    _filter = '(reportdate=^%s^)' % date
                    table = {
                        'date': date,
                        'category': category,
                        'category_type': category_type,
                        'st': st,
                        'sr': sr,
                        'filter': _filter
                    }
                    tables.append(table)
    return tables


def set_page(page_all):
    start_page = 1
    end_page = int(page_all.group(1)) + 1
    page_range = {
        'start_page': start_page,
        'end_page': end_page
    }
    return page_range


def fetch_table(date, category_type, st, sr, _filter, page):
    params = {
        'type': category_type,
        'token': '70f12f2f4f091e459a279469fe49eca5',
        'st': st,
        'sr': sr,
        'p': page,
        'ps': 50,  # 每页显示多少条信息
        'js': 'var LFtlXDqn={pages:(tp),data: (x)}',
        'filter': _filter,
        'rt': 51294261
    }
    url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?'
    response = requests.get(url, params=params).text
    pat = re.compile('var.*?{pages:(\d+),data:.*?')
    page_all = re.search(pat, response)
    pattern = re.compile('var.*?data: (.*)}', re.S)
    items = re.search(pattern, response)
    data = items.group(1)
    data = json.loads(data)
    return page_all, data, page


def batch_store_yjbb(data):
    yjbb = []
    for item in data:
        if item['scode'][0] == '6':
            code = 'sh.' + item['scode']
        else:
            code = 'sz.' + item['scode']
        if item['basiceps'] == '-' or item['basiceps'] == '':
            basic_eps = 0
        else:
            basic_eps = float(item['basiceps'])
        if item['cutbasiceps'] == '-' or item['cutbasiceps'] == '':
            cut_basic_eps = 0
        else:
            cut_basic_eps = float(item['cutbasiceps'])
        if item['totaloperatereve'] == '-' or item['totaloperatereve'] == '':
            total_operate_reve = 0
        else:
            total_operate_reve = float(item['totaloperatereve'])
        if item['ystz'] == '-' or item['ystz'] == '':
            ystz = 0
        else:
            ystz = float(item['ystz'])
        if item['yshz'] == '-' or item['yshz'] == '':
            yshz = 0
        else:
            yshz = float(item['yshz'])
        if item['parentnetprofit'] == '-' or item['parentnetprofit'] == '':
            parent_net_profit = 0
        else:
            parent_net_profit = float(item['parentnetprofit'])
        if item['sjltz'] == '-' or item['sjltz'] == '':
            sjltz = 0
        else:
            sjltz = float(item['sjltz'])
        if item['sjlhz'] == '-' or item['sjlhz'] == '':
            sjlhz = 0
        else:
            sjlhz = float(item['sjlhz'])
        if item['roeweighted'] == '-' or item['roeweighted'] == '':
            roe_weighted = 0
        else:
            roe_weighted = float(item['roeweighted'])
        if item['bps'] == '-' or item['bps'] == '':
            bps = 0
        else:
            bps = float(item['bps'])
        if item['mgjyxjje'] == '-' or item['mgjyxjje'] == '':
            mgjyxjje = 0
        else:
            mgjyxjje = float(item['mgjyxjje'])
        if item['xsmll'] == '-' or item['xsmll'] == '':
            xsmll = 0
        else:
            xsmll = float(item['xsmll'])
        if item['gxl'] == '-' or item['gxl'] == '':
            gxl = 0
        else:
            gxl = float(item['gxl'])

        record = {
            'code': code,
            'name': item['sname'],
            'security_type': item['securitytype'],
            'trade_market': item['trademarket'],
            'latest_notice_date': datetime.datetime.strptime(
                item['latestnoticedate'], '%Y-%m-%dT%H:%M:%S'),
            'report_date': datetime.datetime.strptime(
                item['reportdate'], '%Y-%m-%dT%H:%M:%S'),
            'basic_eps': basic_eps,
            'cut_basic_eps': cut_basic_eps,
            'total_operate_reve': total_operate_reve,
            'ystz': ystz,
            'yshz': yshz,
            'parent_net_profit': parent_net_profit,
            'sjltz': sjltz,
            'sjlhz': sjlhz,
            'roe_weighted': roe_weighted,
            'bps': bps,
            'mgjyxjje': mgjyxjje,
            'xsmll': xsmll,
            'publish_name': item['publishname'],
            'assign_dscrpt': item['assigndscrpt'],
            'gxl': gxl,
            'security_type_code': item['securitytypecode'],
            'trade_market_code': item['trademarketcode'],
            'first_notice_date': datetime.datetime.strptime(
                item['firstnoticedate'], '%Y-%m-%dT%H:%M:%S')
        }
        yjbb.append(record)
    yjbb_query = AStockYJBB.insert_many(yjbb)
    yjbb_query.execute()


def batch_store_zcfzb(data):
    zcfzb = []
    for item in data:
        if item['scode'][0] == '6':
            code = 'sh.' + item['scode']
        else:
            code = 'sz.' + item['scode']
        if item['dataajusttype'] == '-' or item['dataajusttype'] == '':
            data_a_just_type = 0
        else:
            data_a_just_type = int(item['dataajusttype'])
        if item['sumasset'] == '-' or item['sumasset'] == '':
            sum_asset = 0
        else:
            sum_asset = float(item['sumasset'])
        if item['fixedasset'] == '-' or item['fixedasset'] == '':
            fixed_asset = 0
        else:
            fixed_asset = float(item['fixedasset'])
        if item['monetaryfund'] == '-' or item['monetaryfund'] == '':
            monetary_fund = 0
        else:
            monetary_fund = float(item['monetaryfund'])
        if item['monetaryfund_tb'] == '-' or item['monetaryfund_tb'] == '':
            monetary_fund_tb = 0
        else:
            monetary_fund_tb = float(item['monetaryfund_tb'])
        if item['accountrec'] == '-' or item['accountrec'] == '':
            account_rec = 0
        else:
            account_rec = float(item['accountrec'])
        if item['accountrec_tb'] == '-' or item['accountrec_tb'] == '':
            account_rec_tb = 0
        else:
            account_rec_tb = float(item['accountrec_tb'])
        if item['inventory'] == '-' or item['inventory'] == '':
            inventory = 0
        else:
            inventory = float(item['inventory'])
        if item['inventory_tb'] == '-' or item['inventory_tb'] == '':
            inventory_tb = 0
        else:
            inventory_tb = float(item['inventory_tb'])

        if item['sumliab'] == '-' or item['sumliab'] == '':
            sum_liab = 0
        else:
            sum_liab = float(item['sumliab'])
        if item['accountpay'] == '-' or item['accountpay'] == '':
            account_pay = 0
        else:
            account_pay = float(item['accountpay'])
        if item['accountpay_tb'] == '-' or item['accountpay_tb'] == '':
            account_pay_tb = 0
        else:
            account_pay_tb = float(item['accountpay_tb'])
        if item['advancereceive'] == '-' or item['advancereceive'] == '':
            advance_receive = 0
        else:
            advance_receive = float(item['advancereceive'])
        if item['advancereceive_tb'] == '-' or item['advancereceive_tb'] == '':
            advance_receive_tb = 0
        else:
            advance_receive_tb = float(item['advancereceive_tb'])
        if item['sumshequity'] == '-' or item['sumshequity'] == '':
            sum_sh_equity = 0
        else:
            sum_sh_equity = float(item['sumshequity'])
        if item['sumshequity_tb'] == '-' or item['sumshequity_tb'] == '':
            sum_sh_equity_tb = 0
        else:
            sum_sh_equity_tb = float(item['sumshequity_tb'])
        if item['tsatz'] == '-' or item['tsatz'] == '':
            tsatz = 0
        else:
            tsatz = float(item['tsatz'])
        if item['tdetz'] == '-' or item['tdetz'] == '':
            tdetz = 0
        else:
            tdetz = float(item['tdetz'])
        if item['ld'] == '-' or item['ld'] == '':
            ld = 0
        else:
            ld = float(item['ld'])
        if item['zcfzl'] == '-' or item['zcfzl'] == '':
            zcfzl = 0
        else:
            zcfzl = float(item['zcfzl'])
        if item['cashanddepositcbank'] == '-' or item[
            'cashanddepositcbank'] == '':
            cash_and_deposit_c_bank = 0
        else:
            cash_and_deposit_c_bank = float(item['cashanddepositcbank'])
        if item['cashanddepositcbank_tb'] == '-' or item[
            'cashanddepositcbank_tb'] == '':
            cash_and_deposit_c_bank_tb = 0
        else:
            cash_and_deposit_c_bank_tb = float(item['cashanddepositcbank_tb'])
        if item['loanadvances'] == '-' or item['loanadvances'] == '':
            loan_advances = 0
        else:
            loan_advances = float(item['loanadvances'])
        if item['loanadvances_tb'] == '-' or item['loanadvances_tb'] == '':
            loan_advances_tb = 0
        else:
            loan_advances_tb = float(item['loanadvances_tb'])
        if item['saleablefasset'] == '-' or item['saleablefasset'] == '':
            saleable_f_asset = 0
        else:
            saleable_f_asset = float(item['saleablefasset'])
        if item['saleablefasset_tb'] == '-' or item['saleablefasset_tb'] == '':
            saleable_f_asset_tb = 0
        else:
            saleable_f_asset_tb = float(item['saleablefasset_tb'])
        if item['borrowfromcbank'] == '-' or item['borrowfromcbank'] == '':
            borrow_from_bank = 0
        else:
            borrow_from_bank = float(item['borrowfromcbank'])
        if item['borrowfromcbank_tb'] == '-' or item[
            'borrowfromcbank_tb'] == '':
            borrow_from_bank_tb = 0
        else:
            borrow_from_bank_tb = float(item['borrowfromcbank_tb'])
        if item['acceptdeposit'] == '-' or item['acceptdeposit'] == '':
            accept_deposit = 0
        else:
            accept_deposit = float(item['acceptdeposit'])
        if item['acceptdeposit_tb'] == '-' or item['acceptdeposit_tb'] == '':
            accept_deposit_tb = 0
        else:
            accept_deposit_tb = float(item['acceptdeposit_tb'])
        if item['sellbuybackfasset'] == '-' or item['sellbuybackfasset'] == '':
            sell_buy_back_f_asset = 0
        else:
            sell_buy_back_f_asset = float(item['sellbuybackfasset'])
        if item['sellbuybackfasset_tb'] == '-' or item[
            'sellbuybackfasset_tb'] == '':
            sell_buy_back_f_asset_tb = 0
        else:
            sell_buy_back_f_asset_tb = float(item['sellbuybackfasset_tb'])
        if item['settlementprovision'] == '-' or item[
            'settlementprovision'] == '':
            settlement_provision = 0
        else:
            settlement_provision = float(item['settlementprovision'])
        if item['settlementprovision_tb'] == '-' or item[
            'settlementprovision_tb'] == '':
            settlement_provision_tb = 0
        else:
            settlement_provision_tb = float(item['settlementprovision_tb'])
        if item['borrowfund'] == '-' or item['borrowfund'] == '':
            borrow_fund = 0
        else:
            borrow_fund = float(item['borrowfund'])
        if item['borrowfund_tb'] == '-' or item['borrowfund_tb'] == '':
            borrow_fund_tb = 0
        else:
            borrow_fund_tb = float(item['borrowfund_tb'])
        if item['agenttradesecurity'] == '-' or item[
            'agenttradesecurity'] == '':
            agent_trade_security = 0
        else:
            agent_trade_security = float(item['agenttradesecurity'])
        if item['agenttradesecurity_tb'] == '-' or item[
            'agenttradesecurity_tb'] == '':
            agent_trade_security_tb = 0
        else:
            agent_trade_security_tb = float(item['agenttradesecurity_tb'])
        if item['premiumrec'] == '-' or item['premiumrec'] == '':
            premium_rec = 0
        else:
            premium_rec = float(item['premiumrec'])
        if item['premiumrec_tb'] == '-' or item['premiumrec_tb'] == '':
            premium_rec_tb = 0
        else:
            premium_rec_tb = float(item['premiumrec_tb'])
        if item['stborrow'] == '-' or item['stborrow'] == '':
            st_borrow = 0
        else:
            st_borrow = float(item['stborrow'])
        if item['stborrow_tb'] == '-' or item['stborrow_tb'] == '':
            st_borrow_tb = 0
        else:
            st_borrow_tb = float(item['stborrow_tb'])
        if item['premiumadvance'] == '-' or item['premiumadvance'] == '':
            premium_advance = 0
        else:
            premium_advance = float(item['premiumadvance'])
        if item['premiumadvance_tb'] == '-' or item['premiumadvance_tb'] == '':
            premium_advance_tb = 0
        else:
            premium_advance_tb = float(item['premiumadvance_tb'])

        record = {
            'code': code,
            'hy_code': item['hycode'],
            'company_code': item['companycode'],
            'name': item['sname'],
            'publish_name': item['publishname'],
            'mkt': item['mkt'],
            'report_time_type_code': item['reporttimetypecode'],
            'combine_type_code': item['combinetypecode'],
            'data_a_just_type': data_a_just_type,
            'notice_date': datetime.datetime.strptime(
                item['noticedate'], '%Y-%m-%dT%H:%M:%S'),
            'report_date': datetime.datetime.strptime(
                item['reportdate'], '%Y-%m-%dT%H:%M:%S'),
            'sum_asset': sum_asset,
            'fixed_asset': fixed_asset,
            'monetary_fund': monetary_fund,
            'monetary_fund_tb': monetary_fund_tb,
            'account_rec': account_rec,
            'account_rec_tb': account_rec_tb,
            'inventory': inventory,
            'inventory_tb': inventory_tb,
            'sum_liab': sum_liab,
            'account_pay': account_pay,
            'account_pay_tb': account_pay_tb,
            'advance_receive': advance_receive,
            'advance_receive_tb': advance_receive_tb,
            'sum_sh_equity': sum_sh_equity,
            'sum_sh_equity_tb': sum_sh_equity_tb,
            'tsatz': tsatz,
            'tdetz': tdetz,
            'ld': ld,
            'zcfzl': zcfzl,
            'cash_and_deposit_c_bank': cash_and_deposit_c_bank,
            'cash_and_deposit_c_bank_tb': cash_and_deposit_c_bank_tb,
            'loan_advances': loan_advances,
            'loan_advances_tb': loan_advances_tb,
            'saleable_f_asset': saleable_f_asset,
            'saleable_f_asset_tb': saleable_f_asset_tb,
            'borrow_from_bank': borrow_from_bank,
            'borrow_from_bank_tb': borrow_from_bank_tb,
            'accept_deposit': accept_deposit,
            'accept_deposit_tb': accept_deposit_tb,
            'sell_buy_back_f_asset': sell_buy_back_f_asset,
            'sell_buy_back_f_asset_tb': sell_buy_back_f_asset_tb,
            'settlement_provision': settlement_provision,
            'settlement_provision_tb': settlement_provision_tb,
            'borrow_fund': borrow_fund,
            'borrow_fund_tb': borrow_fund_tb,
            'agent_trade_security': agent_trade_security,
            'agent_trade_security_tb': agent_trade_security_tb,
            'premium_rec': premium_rec,
            'premium_rec_tb': premium_rec_tb,
            'st_borrow': st_borrow,
            'st_borrow_tb': st_borrow_tb,
            'premium_advance': premium_advance,
            'premium_advance_tb': premium_advance_tb,
            'eu_time': datetime.datetime.strptime(
                item['eutime'], '%Y-%m-%dT%H:%M:%S')
        }
        zcfzb.append(record)
    zcfzb_query = AStockZCFZB.insert_many(zcfzb)
    zcfzb_query.execute()


def batch_store_lrb(data):
    lrb = []
    for item in data:
        if item['scode'][0] == '6':
            code = 'sh.' + item['scode']
        else:
            code = 'sz.' + item['scode']
        if item['dataajusttype'] == '-' or item['dataajusttype'] == '':
            data_a_just_type = 0
        else:
            data_a_just_type = int(item['dataajusttype'])
        if item['parentnetprofit'] == '-' or item['parentnetprofit'] == '':
            parent_net_profit = 0
        else:
            parent_net_profit = float(item['parentnetprofit'])
        if item['totaloperatereve'] == '-' or item['totaloperatereve'] == '':
            total_operate_reve = 0
        else:
            total_operate_reve = float(item['totaloperatereve'])
        if item['totaloperateexp'] == '-' or item['totaloperateexp'] == '':
            total_operate_exp = 0
        else:
            total_operate_exp = float(item['totaloperateexp'])
        if item['totaloperateexp_tb'] == '-' or item[
            'totaloperateexp_tb'] == '':
            total_operate_exp_tb = 0
        else:
            total_operate_exp_tb = float(item['totaloperateexp_tb'])
        if item['operateexp'] == '-' or item['operateexp'] == '':
            operate_exp = 0
        else:
            operate_exp = float(item['operateexp'])
        if item['operateexp_tb'] == '-' or item['operateexp_tb'] == '':
            operate_exp_tb = 0
        else:
            operate_exp_tb = float(item['operateexp_tb'])
        if item['saleexp'] == '-' or item['saleexp'] == '':
            sale_exp = 0
        else:
            sale_exp = float(item['saleexp'])
        if item['manageexp'] == '-' or item['manageexp'] == '':
            manage_exp = 0
        else:
            manage_exp = float(item['manageexp'])
        if item['financeexp'] == '-' or item['financeexp'] == '':
            finance_exp = 0
        else:
            finance_exp = float(item['financeexp'])
        if item['operateprofit'] == '-' or item['operateprofit'] == '':
            operate_profit = 0
        else:
            operate_profit = float(item['operateprofit'])
        if item['sumprofit'] == '-' or item['sumprofit'] == '':
            sum_profit = 0
        else:
            sum_profit = float(item['sumprofit'])
        if item['incometax'] == '-' or item['incometax'] == '':
            income_tax = 0
        else:
            income_tax = float(item['incometax'])
        if item['operatereve'] == '-' or item['operatereve'] == '':
            operate_reve = 0
        else:
            operate_reve = float(item['operatereve'])
        if item['intnreve'] == '-' or item['intnreve'] == '':
            intn_reve = 0
        else:
            intn_reve = float(item['intnreve'])
        if item['intnreve_tb'] == '-' or item['intnreve_tb'] == '':
            intn_reve_tb = 0
        else:
            intn_reve_tb = float(item['intnreve_tb'])
        if item['commnreve'] == '-' or item['commnreve'] == '':
            commn_reve = 0
        else:
            commn_reve = float(item['commnreve'])
        if item['commnreve_tb'] == '-' or item['commnreve_tb'] == '':
            commn_reve_tb = 0
        else:
            commn_reve_tb = float(item['commnreve_tb'])
        if item['operatetax'] == '-' or item['operatetax'] == '':
            operate_tax = 0
        else:
            operate_tax = float(item['operatetax'])
        if item['operatemanageexp'] == '-' or item['operatemanageexp'] == '':
            operate_manage_exp = 0
        else:
            operate_manage_exp = float(item['operatemanageexp'])
        if item['commreve_commexp'] == '-' or item['commreve_commexp'] == '':
            comm_reve_comm_exp = 0
        else:
            comm_reve_comm_exp = float(item['commreve_commexp'])
        if item['intreve_intexp'] == '-' or item['intreve_intexp'] == '':
            intn_reve_int_exp = 0
        else:
            intn_reve_int_exp = float(item['intreve_intexp'])
        if item['premiumearned'] == '-' or item['premiumearned'] == '':
            premium_earned = 0
        else:
            premium_earned = float(item['premiumearned'])
        if item['premiumearned_tb'] == '-' or item['premiumearned_tb'] == '':
            premium_earned_tb = 0
        else:
            premium_earned_tb = float(item['premiumearned_tb'])
        if item['investincome'] == '-' or item['investincome'] == '':
            invest_income = 0
        else:
            invest_income = float(item['investincome'])
        if item['surrenderpremium'] == '-' or item['surrenderpremium'] == '':
            surrender_premium = 0
        else:
            surrender_premium = float(item['surrenderpremium'])
        if item['indemnityexp'] == '-' or item['indemnityexp'] == '':
            indemnity_exp = 0
        else:
            indemnity_exp = float(item['indemnityexp'])
        if item['tystz'] == '-' or item['tystz'] == '':
            tystz = 0
        else:
            tystz = float(item['tystz'])
        if item['yltz'] == '-' or item['yltz'] == '':
            yltz = 0
        else:
            yltz = float(item['yltz'])
        if item['sjltz'] == '-' or item['sjltz'] == '':
            sjltz = 0
        else:
            sjltz = float(item['sjltz'])
        if item['kcfjcxsyjlr'] == '-' or item['kcfjcxsyjlr'] == '':
            kcfjcxsyjlr = 0
        else:
            kcfjcxsyjlr = float(item['kcfjcxsyjlr'])
        if item['sjlktz'] == '-' or item['sjlktz'] == '':
            sjlktz = 0
        else:
            sjlktz = float(item['sjlktz'])
        if item['yyzc'] == '-' or item['yyzc'] == '':
            yyzc = 0
        else:
            yyzc = float(item['yyzc'])

        record = {
            'code': code,
            'hy_code': item['hycode'],
            'company_code': item['companycode'],
            'name': item['sname'],
            'publish_name': item['publishname'],
            'report_time_type_code': item['reporttimetypecode'],
            'combine_type_code': item['combinetypecode'],
            'data_a_just_type': data_a_just_type,
            'mkt': item['mkt'],
            'notice_date': datetime.datetime.strptime(
                item['noticedate'], '%Y-%m-%dT%H:%M:%S'),
            'report_date': datetime.datetime.strptime(
                item['reportdate'], '%Y-%m-%dT%H:%M:%S'),
            'parent_net_profit': parent_net_profit,
            'sjlktz': sjlktz,
            'total_operate_reve': total_operate_reve,
            'tystz': tystz,
            'operate_exp': operate_exp,
            'operate_exp_tb': operate_exp_tb,
            'sale_exp': sale_exp,
            'manage_exp': manage_exp,
            'finance_exp': finance_exp,
            'total_operate_exp': total_operate_exp,
            'total_operate_exp_tb': total_operate_exp_tb,
            'operate_profit': operate_profit,
            'sum_profit': sum_profit,
            'income_tax': income_tax,
            'operate_reve': operate_reve,
            'intn_reve': intn_reve,
            'intn_reve_tb': intn_reve_tb,
            'commn_reve': commn_reve,
            'commn_reve_tb': commn_reve_tb,
            'operate_tax': operate_tax,
            'operate_manage_exp': operate_manage_exp,
            'comm_reve_comm_exp': comm_reve_comm_exp,
            'intn_reve_int_exp': intn_reve_int_exp,
            'premium_earned': premium_earned,
            'premium_earned_tb': premium_earned_tb,
            'invest_income': invest_income,
            'surrender_premium': surrender_premium,
            'indemnity_exp': indemnity_exp,
            'yltz': yltz,
            'sjltz': sjltz,
            'kcfjcxsyjlr': kcfjcxsyjlr,
            'eu_time': datetime.datetime.strptime(
                item['eutime'], '%Y-%m-%dT%H:%M:%S'),
            'yyzc': yyzc
        }
        lrb.append(record)
    lrb_query = AStockLRB.insert_many(lrb)
    lrb_query.execute()


def batch_store_xjllb(data):
    xjllb = []
    for item in data:
        if item['scode'][0] == '6':
            code = 'sh.' + item['scode']
        else:
            code = 'sz.' + item['scode']
        if item['dataajusttype'] == '-' or item['dataajusttype'] == '':
            data_a_just_type = 0
        else:
            data_a_just_type = int(item['dataajusttype'])
        if item['netoperatecashflow'] == '-' or item[
            'netoperatecashflow'] == '':
            net_operate_cash_flow = 0
        else:
            net_operate_cash_flow = float(item['netoperatecashflow'])
        if item['netoperatecashflow_zb'] == '-' or item[
            'netoperatecashflow_zb'] == '':
            net_operate_cash_flow_zb = 0
        else:
            net_operate_cash_flow_zb = float(item['netoperatecashflow_zb'])
        if item['salegoodsservicerec'] == '-' or item[
            'salegoodsservicerec'] == '':
            sale_goods_service_rec = 0
        else:
            sale_goods_service_rec = float(item['salegoodsservicerec'])
        if item['salegoodsservicerec_zb'] == '-' or item[
            'salegoodsservicerec_zb'] == '':
            sale_goods_service_rec_zb = 0
        else:
            sale_goods_service_rec_zb = float(item['salegoodsservicerec_zb'])
        if item['employeepay'] == '-' or item['employeepay'] == '':
            employee_pay = 0
        else:
            employee_pay = float(item['employeepay'])
        if item['employeepay_zb'] == '-' or item['employeepay_zb'] == '':
            employee_pay_zb = 0
        else:
            employee_pay_zb = float(item['employeepay_zb'])
        if item['netinvcashflow'] == '-' or item['netinvcashflow'] == '':
            net_inv_cash_flow = 0
        else:
            net_inv_cash_flow = float(item['netinvcashflow'])
        if item['netinvcashflow_zb'] == '-' or item['netinvcashflow_zb'] == '':
            net_inv_cash_flow_zb = 0
        else:
            net_inv_cash_flow_zb = float(item['netinvcashflow_zb'])
        if item['invincomerec'] == '-' or item['invincomerec'] == '':
            inv_income_rec = 0
        else:
            inv_income_rec = float(item['invincomerec'])
        if item['invincomerec_zb'] == '-' or item['invincomerec_zb'] == '':
            inv_income_rec_zb = 0
        else:
            inv_income_rec_zb = float(item['invincomerec_zb'])
        if item['buyfilassetpay'] == '-' or item['buyfilassetpay'] == '':
            buy_fil_asset_pay = 0
        else:
            buy_fil_asset_pay = float(item['buyfilassetpay'])
        if item['buyfilassetpay_zb'] == '-' or item['buyfilassetpay_zb'] == '':
            buy_fil_asset_pay_zb = 0
        else:
            buy_fil_asset_pay_zb = float(item['buyfilassetpay_zb'])
        if item['netfinacashflow'] == '-' or item['netfinacashflow'] == '':
            net_fina_cash_flow = 0
        else:
            net_fina_cash_flow = float(item['netfinacashflow'])
        if item['netfinacashflow_zb'] == '-' or item[
            'netfinacashflow_zb'] == '':
            net_fina_cash_flow_zb = 0
        else:
            net_fina_cash_flow_zb = float(item['netfinacashflow_zb'])
        if item['nicashequi'] == '-' or item['nicashequi'] == '':
            ni_cash_equi = 0
        else:
            ni_cash_equi = float(item['nicashequi'])
        if item['nicashequi_tb'] == '-' or item['nicashequi_tb'] == '':
            ni_cash_equi_zb = 0
        else:
            ni_cash_equi_zb = float(item['nicashequi_tb'])
        if item['niclientdeposit'] == '-' or item['niclientdeposit'] == '':
            ni_client_deposit = 0
        else:
            ni_client_deposit = float(item['niclientdeposit'])
        if item['niclientdeposit_zb'] == '-' or item[
            'niclientdeposit_zb'] == '':
            ni_client_deposit_zb = 0
        else:
            ni_client_deposit_zb = float(item['niclientdeposit_zb'])
        if item['niloanadvances'] == '-' or item['niloanadvances'] == '':
            ni_loan_advances = 0
        else:
            ni_loan_advances = float(item['niloanadvances'])
        if item['niloanadvances_zb'] == '-' or item['niloanadvances_zb'] == '':
            ni_loan_advances_zb = 0
        else:
            ni_loan_advances_zb = float(item['niloanadvances_zb'])
        if item['intandcommrec'] == '-' or item['intandcommrec'] == '':
            intand_comm_rec = 0
        else:
            intand_comm_rec = float(item['nicashequi'])
        if item['intandcommrec_zb'] == '-' or item['intandcommrec_zb'] == '':
            intand_comm_rec_zb = 0
        else:
            intand_comm_rec_zb = float(item['intandcommrec_zb'])
        if item['agentuwsecurityrec'] == '-' or item[
            'agentuwsecurityrec'] == '':
            agent_uw_security_rec = 0
        else:
            agent_uw_security_rec = float(item['agentuwsecurityrec'])
        if item['invpay'] == '-' or item['invpay'] == '':
            inv_pay = 0
        else:
            inv_pay = float(item['invpay'])
        if item['invpay_zb'] == '-' or item['invpay_zb'] == '':
            inv_pay_zb = 0
        else:
            inv_pay_zb = float(item['invpay_zb'])
        if item['cashequibeginning'] == '-' or item['cashequibeginning'] == '':
            cash_equi_beginning = 0
        else:
            cash_equi_beginning = float(item['cashequibeginning'])
        if item['cashequibeginning_zb'] == '-' or item[
            'cashequibeginning_zb'] == '':
            cash_equi_beginning_zb = 0
        else:
            cash_equi_beginning_zb = float(item['cashequibeginning_zb'])
        if item['cashequiending'] == '-' or item['cashequiending'] == '':
            cash_equi_ending = 0
        else:
            cash_equi_ending = float(item['cashequiending'])
        if item['cashequiending_zb'] == '-' or item['cashequiending_zb'] == '':
            cash_equi_ending_zb = 0
        else:
            cash_equi_ending_zb = float(item['cashequiending_zb'])
        if item['premiumrec'] == '-' or item['premiumrec'] == '':
            premium_rec = 0
        else:
            premium_rec = float(item['premiumrec'])
        if item['premiumrec_zb'] == '-' or item['premiumrec_zb'] == '':
            premium_rec_zb = 0
        else:
            premium_rec_zb = float(item['premiumrec_zb'])
        if item['indemnitypay'] == '-' or item['indemnitypay'] == '':
            indemnity_pay = 0
        else:
            indemnity_pay = float(item['indemnitypay'])
        if item['indemnitypay_zb'] == '-' or item['indemnitypay_zb'] == '':
            indemnity_pay_zb = 0
        else:
            indemnity_pay_zb = float(item['indemnitypay_zb'])
        if item['nideposit'] == '-' or item['nideposit'] == '':
            ni_deposit = 0
        else:
            ni_deposit = float(item['nideposit'])
        if item['nideposit_zb'] == '-' or item['nideposit_zb'] == '':
            ni_deposit_zb = 0
        else:
            ni_deposit_zb = float(item['nideposit_zb'])

        record = {
            'code': code,
            'hy_code': item['hycode'],
            'company_code': item['companycode'],
            'name': item['sname'],
            'publish_name': item['publishname'],
            'report_time_type_code': item['reporttimetypecode'],
            'combine_type_code': item['combinetypecode'],
            'data_a_just_type': data_a_just_type,
            'mkt': item['mkt'],
            'notice_date': datetime.datetime.strptime(
                item['noticedate'], '%Y-%m-%dT%H:%M:%S'),
            'report_date': datetime.datetime.strptime(
                item['reportdate'], '%Y-%m-%dT%H:%M:%S'),
            'ni_cash_equi': ni_cash_equi,
            'ni_cash_equi_zb': ni_cash_equi_zb,
            'net_operate_cash_flow': net_operate_cash_flow,
            'net_operate_cash_flow_zb': net_operate_cash_flow_zb,
            'net_inv_cash_flow': net_inv_cash_flow,
            'net_inv_cash_flow_zb': net_inv_cash_flow_zb,
            'net_fina_cash_flow': net_fina_cash_flow,
            'net_fina_cash_flow_zb': net_fina_cash_flow_zb,
            'sale_goods_service_rec': sale_goods_service_rec,
            'sale_goods_service_rec_zb': sale_goods_service_rec_zb,
            'employee_pay': employee_pay,
            'employee_pay_zb': employee_pay_zb,
            'inv_income_rec': inv_income_rec,
            'inv_income_rec_zb': inv_income_rec_zb,
            'buy_fil_asset_pay': buy_fil_asset_pay,
            'buy_fil_asset_pay_zb': buy_fil_asset_pay_zb,
            'ni_client_deposit': ni_client_deposit,
            'ni_client_deposit_zb': ni_client_deposit_zb,
            'ni_loan_advances': ni_loan_advances,
            'ni_loan_advances_zb': ni_loan_advances_zb,
            'intand_comm_rec': intand_comm_rec,
            'intand_comm_rec_zb': intand_comm_rec_zb,
            'agent_uw_security_rec': agent_uw_security_rec,
            'inv_pay': inv_pay,
            'inv_pay_zb': inv_pay_zb,
            'cash_equi_beginning': cash_equi_beginning,
            'cash_equi_beginning_zb': cash_equi_beginning_zb,
            'cash_equi_ending': cash_equi_ending,
            'cash_equi_ending_zb': cash_equi_ending_zb,
            'premium_rec': premium_rec,
            'premium_rec_zb': premium_rec_zb,
            'indemnity_pay': indemnity_pay,
            'indemnity_pay_zb': indemnity_pay_zb,
            'ni_deposit': ni_deposit,
            'eu_time': datetime.datetime.strptime(
                item['eutime'], '%Y-%m-%dT%H:%M:%S'),
            'ni_deposit_zb': ni_deposit_zb
        }
        xjllb.append(record)
    xjllb_query = AStockXJLLB.insert_many(xjllb)
    xjllb_query.execute()


def main():
    tables = set_table()
    for table in tables:
        date = table.get('date')
        category = table.get('category')
        category_type = table.get('category_type')
        st = table.get('st')
        sr = table.get('sr')
        _filter = table.get('filter')
        constant = fetch_table(date, category_type, st, sr, _filter, 1)
        page_all = constant[0]
        page_range = set_page(page_all)
        start_page = page_range.get('start_page')
        end_page = page_range.get('end_page')
        for page in range(start_page, end_page):
            res = fetch_table(date, category_type, st, sr, _filter, page)
            data = res[1]
            page = res[2]
            for item in data:
                print(category)
                print(item)
                return


if __name__ == '__main__':
    main()
