from flask import Flask
from stockCollector import StockCollector
from period_task import PeriodTask
import signal
from websockets import WebSocketServerProtocol

app = Flask(__name__)


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

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
