import sqlite3
from mason.globals import get_settings

class Database:
    _connection = None

    @classmethod
    def connect(cls):
        settings = get_settings()
        db_config = settings.DATABASE

        if db_config["ENGINE"] == "sqlite":
            cls._connection = sqlite3.connect(db_config["NAME"], check_same_thread=False)
            cls._connection.row_factory = sqlite3.Row
        else:
            raise NotImplementedError("Only SQLite supported right now")

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            cls.connect()
        return cls._connection

    @classmethod
    def execute(cls, query, params=()):
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur