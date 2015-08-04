from flask import Flask, render_template
from stockCollector import StockCollector
from period_task import PeriodTask
from socket_server import SocketServer
import signal
import threading
from websockets import WebSocketServerProtocol

app = Flask(__name__)
# app.debug = True

# define period tasks
pt = PeriodTask()
sc = StockCollector()
pt.regist_task('getStockName', 1, sc.get_stock_name)
# pt.run_task('getStockName')


# signal capture
def onsignal_int(a,b):
    print('收到SIGTERM信号')
    pt.stop_all_task()
    exit(0)
signal.signal(signal.SIGINT, onsignal_int)


# add a thread to run the websocket server
def run_websocket_svr():
    socket_svr = SocketServer()
    socket_svr.start()


def web_socket_svr():
    t = threading.Thread(target=run_websocket_svr)
    t.setDaemon(True)
    t.start()

@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == '__main__':
    web_socket_svr()
    app.run(host='0.0.0.0', port=3001)