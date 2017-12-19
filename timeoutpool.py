#! /usr/bin/python3
"""
mysql db pool
"""
from queue import Queue
import pymysql
import time
from threading import Event, Thread


def close_pool(pool):
    while 1:
        s = pool.lock.wait(timeout=pool.timeout)
        if not s:
            cf = pool.close()
            if not cf:
                continue
            else:
                break
        else:
            pool.lock.clear()


class SimpleConnPool:
    def __init__(self, conf, pool_size, auto_close=False, timeout=10):
        self.config = conf
        self.pool = Queue(maxsize=pool_size)
        self.pool_size = pool_size
        self.status = 0
        self.auto_cls = auto_close
        self.timeout = timeout
        self.lock = Event()
        if self.auto_cls:
            self.__auto_close()

    def close(self):
        flag = self.pool.full()
        if flag:
            while not self.pool.empty():
                self.pool.get().close()
            self.status = 0
        return flag

    def __full_pool(self):
        for _ in range(0, self.pool_size):
            conn_ = pymysql.connect(**self.config)
            self.pool.put_nowait(conn_)

    def check_connect(self, db):
        try:
            db.ping()
        except Exception:
            db = pymysql.connect(**self.config)
        return db

    def __auto_close(self):
        worker = Thread(target=close_pool, args=(self,))
        worker.setDaemon(True)
        worker.start()

    def get(self):
        if self.status == 0:
            self.__full_pool()
            self.status = 1
        else:
            self.lock.set()
        db = self.pool.get(True)
        db = self.check_connect(db)
        return db

    def restore(self, db):
        self.pool.put_nowait(db)


if __name__ == "__main__":
    dd = {
        'user': 'user_name', 'password': 'password', 'host': '127.0.0.1', 'db': 'test', 'charset': 'utf8', 'autocommit': True
    }
    conn_pool = SimpleConnPool(dd, 4, auto_close=True)

    conn_db = conn_pool.get()
    conn_pool.restore(conn_db)

    conn_db2 = conn_pool.get()
    conn_pool.restore(conn_db2)

    conn_db2 = conn_pool.get()
    conn_pool.restore(conn_db2)

    print('first')
    time.sleep(25)
