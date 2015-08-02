__author__ = 'apple'

import threading


class PeriodTask:
    tasks = {}
    stop = {}

    def __init__(self):
        self.tasks = {}
        self.stop = {}
        return

    def timer_start(self, name, timeInterval, cb, arg):
        cb(arg)
        if name in self.stop and self.stop[name] is True:
            return
        del self.tasks[name]
        self.regist_task(name, timeInterval, cb, arg)
        self.tasks[name].start()
        return

    def regist_task(self, name, timeInterval, cb, arg=None):
        args = [name, timeInterval, cb, arg]
        t = threading.Timer(timeInterval, self.timer_start, args)
        self.tasks[name] = t
        self.stop[name] = False
        return

    def remove_task(self, name):
        del self.tasks[name]
        return

    def run_task(self, name):
        self.tasks[name].start()
        return

    def stop_task(self, name):
        self.tasks[name].cancel()
        self.stop[name] = True
        return

    def stop_all_task(self):
        for name in self.tasks:
            self.tasks[name].cancel()
            self.stop[name] = True
