import json
import re
import requests


def set_table():
    tables = []
    for year in range(2007, 2021):
        for quarter in range(1, 5):
            month = '{:02d}'.format(quarter * 3)
            if (month == '06') or (month == '09'):
                day = 30
            else:
                day = 31
            date = '{}-{}-{}'.format(year, month, day)

            categories = ['YJBB', 'YJKB', 'YJYG', 'YYPL', 'ZCFZB', 'LRB',
                          'XJLLB']
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
    # print(page_all.group(1))
    pattern = re.compile('var.*?data: (.*)}', re.S)
    items = re.search(pattern, response)
    data = items.group(1)
    data = json.loads(data)
    return page_all, data, page


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
