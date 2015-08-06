__author__ = 'apple'

import requests
import json
import re
import time


class StockCollector:
    stocks = []
    result = {}
    raw_data = ''
    def __init__(self):
        self.stocks = []
        self.result = {}
        self.raw_data = ''

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

############################################################################
    '''
    第一版工作方式：
        1.通过get_stock_names获取所有的股票代号
        2.通过get_stocks一个接一个获取股票当前数据
        3.每一个都处理完成后做成最后的返回数据回调
        4.回调函数中通知所有连接的用户
    缺点:
        1.同步，所有请求依次执行，等待的时间为2500多个请求之和
        2.新浪接口是支持一次请求同时获取多个的实测500个没有问题,一次一个的方式效率太低
    时间:
        1.每次时间5分钟以上
    优化点:
        1.一次请求多个股票数据(200个)
        2.使用线程池并行加快速度
    '''
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

###############################################################
    '''
    第二版工作方式：
        1.通过get_stock_names获取所有的股票代号
        2.每次200个股票同时请求，请求14次，依次执行
        3.合并所有请求的数据并计算
        4.回调函数中通知所有连接的用户
    时间:
        1.每次时间10秒左右
    优化点:
        2.使用线程池并行加快速度
    '''
    def calculate_up_down_2(self, cb=None):
        raw_data = self.get_stock_patch()
        raw_datas = raw_data.split(';')
        computed = {}
        upMax = []
        downMax = []
        for data in raw_datas:
            if len(data) < 10:
                raw_datas.remove(data)
                continue
            data = data.replace('_', '=').replace('"', '=').split('=')
            stock_id = data[2]
            stock_data = data[4].split(',')

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
            if change >= 9.99:
                upMax.append(stock_id)
            elif change <= -9.99:
                downMax.append(stock_id)
        ret = {}
        ret['computed'] = computed
        ret['upMax'] = upMax
        ret['downMax'] = downMax
        ret['timestamp'] = time.time()
        self.result = ret
        if cb is not None:
            cb()
        return ret

    def cal_one_stock(self, id, data):
        return

    def get_stock_patch(self):
        self.raw_data = ''
        path = 'http://hq.sinajs.cn/list='
        str = ''
        c = 0
        for i in self.get_stock_names():
            c = c + 1
            str += i
            str += ','
            if c < 200:
                continue
            r = requests.get(path + str)
            self.raw_data += r.text
            c = 0
            str = ''
        r = requests.get(path + str)
        self.raw_data += r.text
        return self.raw_data


if __name__ == '__main__':
    sc = StockCollector()
    sc.calculate_up_down_2()