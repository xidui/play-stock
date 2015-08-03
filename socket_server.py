__author__ = 'apple'
import asyncio
import websockets
import json
import re
from stockCollector import *


class SocketServer:
    sockets = []

    def __init__(self):
        self.sockets = []
        return

    @asyncio.coroutine
    def proceed(self, websocket, path):
        self.sockets.append(websocket)
        while True:
            data = yield from websocket.recv()
            if not data:
                break
            data = json.loads(re.compile(r'(?<=[{,])\w+').sub("\"\g<0>\"", data))
            if 'getStock' in data:
                stocks = data['getStock']
                for stock in StockCollector.get_single_stock(stocks):
                    stock_data = stock.split('"')[1].split(',')
                    yield from websocket.send(str(stock_data))
        self.sockets.remove(websocket)

    def start(self):
        start_server = websockets.serve(self.proceed, '127.0.0.1', 8765)
        print('socket server listen on port 8765')
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    socket_svr = SocketServer()
    socket_svr.start()