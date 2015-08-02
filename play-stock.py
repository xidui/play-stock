from flask import Flask
import mongo_proxy
from stockCollector import StockCollector
from period_task import PeriodTask

app = Flask(__name__)


# define period tasks
pt = PeriodTask()
sc = StockCollector()
pt.regist_task('getStockName', 1, sc.get_stock_name)
pt.run_task('getStockName')


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
