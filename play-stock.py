from flask import Flask, render_template
from stockCollector import StockCollector
from socket_server import SocketServer
import signal
import threading
from websockets import WebSocketServerProtocol
from config import get_web_server_port

app = Flask(__name__)
# app.debug = True

# signal capture
def onsignal_int(a,b):
    # print('收到SIGTERM信号')
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
def root():
    return render_template('index.html')


if __name__ == '__main__':
    web_socket_svr()
    app.run(host='0.0.0.0', port=get_web_server_port())