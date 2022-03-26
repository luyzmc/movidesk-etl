import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')


class DB:

    def __init__(self):
        self.__connection = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

    def __del__(self):
        if self.__connection is not None:
            self.__connection.close()

    def fetchone(self, query: str):
        cur = None
        result = None
        try:
            cur = self.__connection.cursor()
            cur.execute(query)
            result = cur.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if cur is not None:
                cur.close()

        return result

    def execute(self, query: str):
        cur = None
        try:
            cur = self.__connection.cursor()
            cur.execute(query)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if cur is not None:
                cur.close()

    def commit(self):
        self.__connection.commit()

    @staticmethod
    def connect():
        return DB()

    def disconect(self):
        del self
