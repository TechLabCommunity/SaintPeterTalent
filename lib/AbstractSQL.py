from mysql import connector
from enum import IntEnum
import xml.etree.ElementTree as ET

class FetchType(IntEnum):
    ONE = 0,
    ALL = 1,
    EXECUTE = 2


class AbstractSQL:

    PATH_CONFIG = 'lib/config.xml'

    @staticmethod
    def fetch_execute_one(query, params):
        return AbstractSQL.fetch_execute(query, params, FetchType.ONE)

    @staticmethod
    def fetch_execute_all(query, params):
        return AbstractSQL.fetch_execute(query, params, FetchType.ALL)

    @staticmethod
    def execute_commit(query, params):
        return AbstractSQL.fetch_execute(query, params, FetchType.EXECUTE)

    @staticmethod
    def fetch_execute(query, params, fetch_type):
        cnx = AbstractSQL.get_connection()
        cursor = cnx.cursor()
        cursor.execute(query, params)
        res = None
        if fetch_type == FetchType.ONE:
            res = cursor.fetchone()
        elif fetch_type == FetchType.ALL:
            res = cursor.fetchall()
        else:
            cnx.commit()
        cnx.close()
        return res

    @staticmethod
    def get_query_by_name(name):
        query = "SELECT Query FROM access_queries WHERE Name = %s";
        row = AbstractSQL.fetch_execute_one(query, (name,))
        if row is None:
            raise ValueError('Query not found into DB.')
        return row[0]

    @staticmethod
    def get_connection():
        db = ET.parse(AbstractSQL.PATH_CONFIG).getroot()[0]
        return connector.connect(user=db.find('user').text, passwd=db.find('passwd').text, host=db.find('host').text, db=db.find('db').text,
                                 port=int(db.find('port').text))