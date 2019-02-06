import pymongo
from sshtunnel import SSHTunnelForwarder


class MongoServices:

    def __init__(self):
        pass

    def getDb(self, db):
        return pymongo.MongoClient().get_database(db)

    def getServerDb(self,  ssh_server:SSHTunnelForwarder, db_name):

        if not ssh_server.is_active:
            ssh_server.start()

        client = pymongo.MongoClient('127.0.0.1', ssh_server.local_bind_port)
        return client.get_database(db_name)