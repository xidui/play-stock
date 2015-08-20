__author__ = 'apple'
from pymongo import MongoClient
from config import get_web_server_port


def get_db():
    # 建立连接
    client = MongoClient(get_web_server_port())
    # test,还有其他写法
    db = client.stock
    return db


def get_collection(db, name):
    # 选择集合(mongo中collection和database都是lazy创建的，具体可以google下)
    collection = db[name]
    return collection


def insert_one_doc(collection, doc):
    # 插入一个document
    return collection.insert(doc)

if __name__ == "__main__":
    db = get_db()
    stock = get_collection(db, 'stock1')
    for i in range(10000):
        insert_one_doc(stock, {'name': i})
        if i % 500 == 0:
            print(i)

