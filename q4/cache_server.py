import socket
import threading
import sqlite3

# use born pattern to have a singleton
class Cache(object):
    DATAFILE = 'cache.db'
    DDL = """create table if not exists 
    cached ( hash_key integer primary key
    ,payload string 
    ,created datetime default current_timestamp
    )"""
    SELECT_SQL = "select payload,created from cached where hash_key = {0} ;".format
    DELETE_SQL = "delete from cached where hash_key = {0} ;".format
    UPSERT_SQL = "insert or replace into cached (hash_key, payload) values ({0},{1})".format
    _shared_state = {}


    def __init__(self,datafile=None):
        self.__dict__ = self._shared_state
        if self._shared_state.get('_conn') is None:
            self._shared_state['_datafile'] = datafile if datafile else Cache.DATAFILE
            self._shared_state['_conn'] = sqlite3.connect(self._shared_state['_datafile'], check_same_thread=False)
            self._shared_state['_data'] = {}
        Cache._ensure_tables()

    @classmethod
    def _ensure_tables(cls):
        cursor = cls._shared_state['_conn'].cursor()
        cursor.execute(cls.DDL)
        cls._shared_state['_conn'].commit()

    def store(self, key, value):
        self._data[key] = value

    def delete(self, key):
        hash_key = hash(key)
        del self._data[key]
        cursor = self._conn.cursor()
        cursor.execute(self.DELETE_SQL(hash_key))
        self._conn.commit()

    def get(self, key):
        hash_key = hash(key)
        if self._data.get(key) is None:
            cursor = self._conn.cursor()
            cursor.execute(self.SELECT_SQL(hash_key))
            rows = cursor.fetchall()
            if len(rows) > 0:
                value,_ = rows[0][0]
                self._data[key] = value
        return self._data.get(key)

    def persist(self, key, value=None):
        if value is None:
            value = self.get(key)
        if value is not None:
            hash_key = hash(key)
            cursor = self._conn.cursor()
            cursor.execute(self.UPSERT_SQL(hash_key, value))
            self._conn.commit()
        return value



class CacheServer(object):
    cache = Cache()
    VERBS = ("GET", "SET", "DELETE", "PERSIST")

    def __init__(self):
        pass

    def handle_client_connection(client_socket):
        try:
            request = client_socket.recv(2056)
            request = str(request, 'utf-8')
            request = request.rstrip("\n")
            verb, payload = CacheServer.parse_input(request)
            reply = "ok"
            try:
                if verb not in CacheServer.VERBS:
                    reply = f"Unknown action {verb}"
                elif verb == "GET":
                    key = payload.split(' ')[0]
                    reply = str(CacheServer.cache.get(key))
                elif verb == "SET":
                    key = payload.split(' ')[0]
                    store_value = payload.lstrip(f"{key} ")
                    CacheServer.cache.store(key, store_value)
                    reply = "ok"
                elif verb == "DELETE":
                    key = payload.split(' ')[0]
                    CacheServer.cache.delete(key)
                    reply = "ok"
                else:
                    key = payload.split(' ')[0]
                    CacheServer.cache.persist(key)
            except Exception as e:
                reply = e
            client_socket.send(reply.encode('utf-8'))
        finally:
            client_socket.close()

    @staticmethod
    def parse_input(msg):
        """ parse input into <VERB> <PAYLOAD>
        VERB SET/GET/DELETE/PERSIST 
        PAYLOAD JSON
        """
        verb = msg.split(' ')[0]
        return (verb, msg.lstrip(f"{verb} "))

    @classmethod
    def server_loop(cls):
        bind_ip = '0.0.0.0'
        bind_port = 12001 
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((bind_ip, bind_port))
        server.listen(5)  # max backlog of connections
        print(f'Listening on {bind_ip}:{bind_port}')
        while True:
            client_sock, address = server.accept()
            client_handler = threading.Thread(
                target=cls.handle_client_connection,
                args=(client_sock,)
            )
            client_handler.start()

if __name__ == '__main__':
    CacheServer.server_loop()
