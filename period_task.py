__author__ = 'apple'

import threading


class PeriodTask:
    tasks = {}

    def __init__(self):
        self.tasks = {}
        return

    def timer_start(self, name, timeInterval, cb, arg):
        cb(arg)
        if name not in self.tasks:
            return
        del self.tasks[name]
        self.regist_task(name, timeInterval, cb, arg)
        self.tasks[name].start()
        return

    def regist_task(self, name, timeInterval, cb, arg=None):
        args = [name, timeInterval, cb, arg]
        t = threading.Timer(timeInterval, self.timer_start, args)
        self.tasks[name] = t
        return

    def remove_task(self, name):
        del self.tasks[name]
        return

    def run_task(self, name):
        self.tasks[name].start()
        return

    def stop_task(self, name):
        self.tasks[name].cancel()

    def stop_all_task(self):
        for name in self.tasks:
            self.tasks[name].cancel()
            del self.tasks[name]
