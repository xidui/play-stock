__author__ = 'apple'

import requests
import json
import re


class StockCollector:
    def __init__(self):
        self.stocks = []

    def get_stock_name(self, args=None):
        path = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
        payload = {
            'page': 1,
            'num': 10000,
            'sort': '',  # ['changepercent'|]
            'asc': 0,
            'node': 'hs_a',  # 沪深A股？
            'symbol': '',
            '_s_r_a': 'page'
        }
        r = requests.get(path, params=payload)

        # 用正则表达式处理不规范的json数据
        re_item = re.compile(r'(?<=[{,])\w+')
        after = re_item.sub("\"\g<0>\"", r.text)
        self.stocks = []
        for stock in json.loads(after):
            self.stocks.append(stock['symbol'])
        self.stocks.sort()
        print(len(self.stocks))
        return

    def get_stocks(self):
        if len(self.stocks) != 0:
            return self.stocks
        return self.get_stock_name()

    @staticmethod
    def get_stocks(stocks):
        for stock in stocks:
            path = 'http://hq.sinajs.cn/list=' + stock
            r = requests.get(path)
            yield stock, r.text