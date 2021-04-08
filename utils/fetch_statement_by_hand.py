import csv
import json
import os
import requests
import re
import time

file_path = 'eastmoney'
if not os.path.exists(file_path):
    os.mkdir(file_path)
os.chdir(file_path)


def set_table():
    # year = int(float(input('请输入要查询的年份(四位数2007-)：\n')))
    # while year < 2007:
    #     year = int(float(input('年份数值输入错误，请重新输入：\n')))

    # quarter = int(float(input('请输入小写数字季度(1:1季报，2-年中报，3：3季报，4-年报)：\n')))
    # while quarter < 1 or quarter > 5:
    #     quarter = int(float(input('季度数值输入错误，请重新输入：\n')))

    # year = 2007
    # year = 2008
    # year = 2009
    # year = 2010
    # year = 2011
    # year = 2012
    # year = 2013
    # year = 2014
    # year = 2015
    # year = 2016
    # year = 2017
    # year = 2018
    # year = 2019
    # year = 2020
    year = 2021
    ######################
    quarter = 1
    # quarter = 2
    # quarter = 3
    # quarter = 4
    ######################
    tables = 1
    # tables = 5
    # tables = 6
    # tables = 7
    quarter = '{:02d}'.format(quarter * 3)

    if (quarter == '06') or (quarter == '09'):
        day = 30
    else:
        day = 31
    date = '{}-{}-{}'.format(year, quarter, day)

    # tables = int(
    #     input(
    #         '请输入查询的报表种类对应的数字(1-业绩报表；2-业绩快报表：3-业绩预告表；4-预约披露时间表；5-资产负债表；6-利润表；7-现金流量表): \n'))
    dict_tables = {1: '业绩报表', 2: '业绩快报表', 3: '业绩预告表',
                   4: '预约披露时间表', 5: '资产负债表', 6: '利润表', 7: '现金流量表'}

    dict = {1: 'YJBB', 2: 'YJKB', 3: 'YJYG',
            4: 'YYPL', 5: 'ZCFZB', 6: 'LRB', 7: 'XJLLB'}
    category = dict[tables]
    print('-' * 7, '开始下载', date, '-', category, '-' * 7)

    # js请求参数里的type，第1-4个表的前缀是'YJBB20_'，后3个表是'CWBB_'
    # 设置set_table()中的type、st、sr、filter参数
    if tables == 1:
        category_type = 'YJBB20_'
        st = 'latestnoticedate'
        sr = -1
        filter = "(securitytypecode in ('058001001','058001002'))(reportdate=^%s^)" % (
            date)
    elif tables == 2:
        category_type = 'YJBB20_'
        st = 'ldate'
        sr = -1
        filter = "(securitytypecode in ('058001001','058001002'))(rdate=^%s^)" % (
            date)
    elif tables == 3:
        category_type = 'YJBB20_'
        st = 'ndate'
        sr = -1
        filter = " (IsLatest='T')(enddate=^2018-06-30^)"
    elif tables == 4:
        category_type = 'YJBB20_'
        st = 'frdate'
        sr = 1
        filter = "(securitytypecode ='058001001')(reportdate=^%s^)" % (date)
    else:
        category_type = 'CWBB_'
        st = 'noticedate'
        sr = -1
        filter = '(reportdate=^%s^)' % (date)

    category_type = category_type + category

    yield {
        'date': date,
        'category': dict_tables[tables],
        'category_type': category_type,
        'st': st,
        'sr': sr,
        'filter': filter
    }


def page_choose(page_all):
    # start_page = int(input('请输入下载起始页数：\n'))
    start_page = 1
    end_page = int(page_all.group(1)) + 1
    # nums = input('请输入要下载的页数，（若需下载全部则按回车）：\n')
    # print('*' * 80)

    # if nums.isdigit():
    #     end_page = start_page + int(nums) + 1
    # elif nums == '':
    #     end_page = int(page_all.group(1)) + 1
    # else:
    #     print('页数输入错误')

    yield {
        'start_page': start_page,
        'end_page': end_page
    }


def get_table(date, category_type, st, sr, filter, page):
    print('\n正在下载第 %s 页表格' % page)
    params = {
        'type': category_type,  # 表格类型
        'token': '70f12f2f4f091e459a279469fe49eca5',
        'st': st,
        'sr': sr,
        'p': page,
        'ps': 50,  # 每页显示多少条信息
        'js': 'var LFtlXDqn={pages:(tp),data: (x)}',
        'filter': filter,
        # 'rt': 51294261  可不用
    }
    url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?'

    response = requests.get(url, params=params).text
    # 确定页数
    pat = re.compile('var.*?{pages:(\d+),data:.*?')
    page_all = re.search(pat, response)

    # 提取出list，可以使用json.dumps和json.loads
    pattern = re.compile('var.*?data: (.*)}', re.S)
    items = re.search(pattern, response)

    data = items.group(1)
    data = json.loads(data)

    return page_all, data, page


def write_header(data, category, date):
    with open('{}-{}.csv'.format(category, date), 'a', encoding='utf_8_sig',
              newline='') as f:
        headers = list(data[0].keys())
        writer = csv.writer(f)
        writer.writerow(headers)


def write_table(data, page, category, date):
    for d in data:
        with open('{}-{}.csv'.format(category, date), 'a', encoding='utf_8_sig',
                  newline='') as f:
            w = csv.writer(f)
            w.writerow(d.values())
    print('\n写入完成第 %s 页表格' % page)


def main(date, category_type, st, sr, filter, page):
    func = get_table(date, category_type, st, sr, filter, page)
    data = func[1]
    page = func[2]
    write_table(data, page, category, date)


if __name__ == '__main__':
    for i in set_table():
        date = i.get('date')
        category = i.get('category')
        category_type = i.get('category_type')
        st = i.get('st')
        sr = i.get('sr')
        filter = i.get('filter')

    constant = get_table(date, category_type, st, sr, filter, 1)
    page_all = constant[0]

    for i in page_choose(page_all):
        start_page = i.get('start_page')
        end_page = i.get('end_page')

    # 写入表头
    write_header(constant[1], category, date)
    start_time = time.time()  # 下载开始时间
    # 爬取表格主程序
    print('总共' + str(end_page - 1) + '页')
    for page in range(start_page, end_page):
        main(date, category_type, st, sr, filter, page)

    end_time = time.time() - start_time  # 结束时间
    print('-' * 7, date, '-', category, '下载完成', '-' * 7)
    print('下载用时: {:.1f} s'.format(end_time))
