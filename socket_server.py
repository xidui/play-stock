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
        print('a new connection comes, total :', len(self.sockets))
        while True:
            data = yield from websocket.recv()
            if not data:
                break
            data = json.loads(re.compile(r'(?<=[{,])\w+').sub("\"\g<0>\"", data))
            if 'getStock' in data:
                stocks = data['getStock']
                for stock_name, stock_data in StockCollector.get_stocks(stocks):
                    ret = {stock_name: stock_data.split('"')[1].split(',')}
                    yield from websocket.send(str(ret))
        self.sockets.remove(websocket)
        print('a connection broken, total :', len(self.sockets))

    def start(self):
        start_server = websockets.serve(self.proceed, '0.0.0.0', 8765)
        print('socket server listen on port 8765')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


# if __name__ == '__main__':
    # socket_svr = SocketServer()
    # socket_svr.start()