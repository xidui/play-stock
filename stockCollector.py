__author__ = 'apple'

import requests
import json
import re
import time


class StockCollector:
    stocks = []
    result = {}
    def __init__(self):
        self.stocks = []
        self.result = {}

    def get_stock_names(self, args=None):
        if len(self.stocks) != 0:
            # print('I have')
            return self.stocks
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
        return self.stocks

    def get_calculated_data(self):
        return self.result

    def calculate_up_down(self, cb=None):
        '''
        {
            timestamp : xxxx,
            upMax : ['sh000001', 'sh000002'],
            downMax : ['sh000003', 'sh000004'],
            computed : {
                'sh000001' : [股票中文名, 涨跌幅, 开盘价, 昨天价, 现价],
                'sh000002' : [股票中文名, 涨跌幅, 开盘价, 昨天价, 现价],
                'sh000003' : [股票中文名, 涨跌幅, 开盘价, 昨天价, 现价]
            }
        }
        '''
        computed = {}
        upMax = []
        downMax = []
        for stock_id, stock_data in self.get_stocks(self.get_stock_names()):
            # if len(computed) == 10:
            #     break
            stock_data = stock_data.split('"')[1].split(',')
            chinesename = stock_data[0]
            begin_price = float(stock_data[1])
            yeste_price = float(stock_data[2])
            curre_price = float(stock_data[3])
            change = (curre_price - yeste_price) / yeste_price * 100
            temp = [
                chinesename,
                change,
                curre_price,
                begin_price,
                yeste_price
            ]
            computed[stock_id] = temp
            if change > 9.9:
                upMax.append(stock_id)
            elif change < -9.9:
                downMax.append(stock_id)
        ret = {}
        ret['computed'] = computed
        ret['upMax'] = upMax
        ret['downMax'] = downMax
        ret['timestamp'] = time.time()
        # print(ret)
        # print(len(upMax))
        # print(len(downMax))
        self.result = ret
        if cb is not None:
            cb()
        return ret

    @staticmethod
    def get_stocks(stocks):
        for stock in stocks:
            path = 'http://hq.sinajs.cn/list=' + stock
            r = requests.get(path)
            yield stock, r.text

if __name__ == '__main__':
    sc = StockCollector()
    for i in sc.get_stock_names():
        print(i)