__author__ = 'apple'
import threading
import queue


class ThreadPool:
    def __init__(self, pool_size=1):
        self.pool_size = pool_size
        self.queue_lock = threading.Lock()
        self.cb_lock = threading.Lock()
        self.workers = queue.Queue()
        self.threads = list()
        for i in range(pool_size):
            thread = threading.Thread(target=self.thread_routine, args=[i])
            self.threads.append(thread)

    def add_worker(self, task, args=None, cb=None):
        self.queue_lock.acquire()
        self.workers.put({
            'worker': task,
            'args': args,
            'cb': cb
        })
        self.queue_lock.release()
        return

    def thread_routine(self, thread_id=None):
        while True:
            # print(str(thread_id) + 'work')
            self.queue_lock.acquire()
            if self.workers.empty():
                self.queue_lock.release()
                # print(str(thread_id) + 'exit')
                exit(0)
            worker = self.workers.get()
            self.queue_lock.release()

            try:
                result = worker['worker'](worker['args'])
                if worker['cb'] is not None:
                    self.cb_lock.acquire()
                    worker['cb'](result)
                    self.cb_lock.release()
            except Exception as err:
                print(err)

    def pool_start(self):
        for thread in self.threads:
            thread.start()

    def pool_join(self):
        for thread in self.threads:
            thread.join()


if __name__ == '__main__':
    def task(num):
        count = 0
        for i in range(num):
            count += i + 1
        return num, count

    def cb(result):
        return
        # print(result)

    tp = ThreadPool(100)
    for i in range(1000):
        tp.add_worker(task, i, cb)
    tp.pool_start()
    tp.pool_join()