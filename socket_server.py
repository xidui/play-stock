__author__ = 'apple'
import asyncio
import websockets
import json
import re
from stockCollector import *
from period_task import PeriodTask


class SocketServer:
    sockets = []
    stock_collector = StockCollector()

    def __init__(self):
        self.sockets = []
        return

    @asyncio.coroutine
    def proceed(self, websocket, path):
        self.sockets.append(websocket)
        print('a new connection comes, total :', len(self.sockets))
        while True:
            data = yield from websocket.recv()
            if not data:
                break
            ret = self.stock_collector.get_calculated_data()
            yield from websocket.send(str(ret))
            # data = json.loads(re.compile(r'(?<=[{,])\w+').sub("\"\g<0>\"", data))
            # if 'fetchData' in data:
            #     ret = self.stock_collector.get_calculated_data()
            #     print(ret)
            #     yield from websocket.send(str(ret))
        self.sockets.remove(websocket)
        print('a connection broken, total :', len(self.sockets))

    def run_stock_collector(self):
        pt = PeriodTask()
        pt.regist_task('calUpDown', 5, self.stock_collector.calculate_up_down_2, self.notify_peer)
        pt.run_task('calUpDown')

    def notify_peer(self):
        ret = self.stock_collector.get_calculated_data()
        print(ret)
        for socket in self.sockets:
            for temp in socket.send(str(ret)):
                # because socket.send is a generator, I have to wrap it in a 'for in'
                print(123) # why this can not be executed?
        print('after callback')
        return

    def start(self):
        self.run_stock_collector()
        start_server = websockets.serve(self.proceed, '0.0.0.0', 8765)
        print('socket server listen on port 8765')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    socket_svr = SocketServer()
    socket_svr.start()