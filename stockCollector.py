__author__ = 'apple'

import requests
import json
import re
import time
from ThreadPool import ThreadPool


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
        if len(self.result) > 0:
            if not self.is_in_business_time(time.time()):
                return self.result
        '''
        {
            timestamp: xxxx,
            buy_total: buy_total,
            sell_total: sell_total,
            upMax : ['sh000001', 'sh000002'],
            downMax : ['sh000003', 'sh000004'],
            stop: ['shxxxxxx', 'shxxxxxx'],
            computed : {
                'sh000001' : [股票中文名, 涨跌幅, 开盘价, 昨天价, 现价],
                'sh000002' : [股票中文名, 涨跌幅, 开盘价, 昨天价, 现价],
                'sh000003' : [股票中文名, 涨跌幅, 开盘价, 昨天价, 现价]
            }
        }
        '''
        raw_data = self.get_stock_patch()
        raw_datas = raw_data.split(';')
        computed = {}
        upMax = []
        downMax = []
        stop = []
        up = []
        down = []

        buy_total = 0
        sell_total = 0

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
                begin_price,
                yeste_price,
                curre_price
            ]
            computed[stock_id] = temp
            if curre_price == 0:
                stop.append(stock_id)
            else:
                if change > 0:
                    up.append(stock_id)
                    if change > 9.99:
                        upMax.append(stock_id)
                elif change < 0:
                    down.append(stock_id)
                    if change < -9.99:
                        downMax.append(stock_id)
                buy_total += int(stock_data[10]) / 100
                buy_total += int(stock_data[12]) / 100
                buy_total += int(stock_data[14]) / 100

                sell_total += int(stock_data[20]) / 100
                sell_total += int(stock_data[22]) / 100
                sell_total += int(stock_data[24]) / 100

        ret = {}
        # ret['computed'] = computed
        ret['upMax'] = upMax
        ret['downMax'] = downMax
        ret['stop'] = stop
        ret['down'] = down
        ret['up'] = up
        ret['timestamp'] = time.time()
        ret['buy_total'] = buy_total
        ret['sell_total'] = sell_total
        self.result = ret
        if cb is not None:
            cb()
        return ret

    @staticmethod
    def is_in_business_time(timestamp):
        try:
            current_time = time.strftime('%H:%M:%S', time.gmtime(timestamp))
            current_time = time.strptime(current_time, '%H:%M:%S')
            start_time_morning = time.strptime('01:30:00', "%H:%M:%S")
            end_time_morning = time.strptime('03:30:00', "%H:%M:%S")
            start_time_afternoon = time.strptime('5:00:00', "%H:%M:%S")
            end_time_afternoon = time.strptime('7:00:00', "%H:%M:%S")
            if current_time >= start_time_morning and current_time <= end_time_morning:
                return True
            if current_time >= start_time_afternoon and current_time <= end_time_afternoon:
                return True
            return False
        except Exception as err:
            return True

    @staticmethod
    def thread_task(path):
        r = requests.get(str(path))
        return r.text

    def thread_task_cb(self, result):
        self.raw_data += result
        return

    def get_stock_patch(self):
        print('get_stock_patch')
        self.raw_data = ''
        tp = ThreadPool(10)
        path = 'http://hq.sinajs.cn/list='
        str = ''
        c = 0
        for i in self.get_stock_names():
            c = c + 1
            str += i
            str += ','
            if c < 200:
                continue
            tp.add_worker(self.thread_task, path + str, self.thread_task_cb)
            str = ''
            c = 0
        if len(str) > 0:
            tp.add_worker(self.thread_task, path + str, self.thread_task_cb)
        tp.pool_start()
        tp.pool_join()
        print('get_stock_patch_done')
        return self.raw_data


if __name__ == '__main__':
    sc = StockCollector()
    sc.calculate_up_down_2()