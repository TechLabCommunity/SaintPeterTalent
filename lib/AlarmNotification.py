from telnetlib import Telnet
from lib.AbstractSQL import AbstractSQL
from lib.SPDbCall import TypeAlarmAction
from enum import IntEnum
import json

class AlarmAction(IntEnum):
    ACTIVATE = 0,
    DEACTIVATE = 1,
    STATUS = 2

class AlarmNotification(Telnet):

    TIMEOUT = 3
    is_open = False

    def __init__(self, name):
        self.name = name
        self.token, host, port = self.get_info_alarm(name)
        try:
            super().__init__(host, port, self.TIMEOUT)
            self.is_open = True
        except:
            AbstractSQL.execute_commit(self.get_insert_query(), (self.name, 'ERROR CONNECTION', 1))
            raise ConnectionError('No connection')

    def send_what_to_do(self, action):
        try:
            self.write((json.dumps(self.get_request(action, self.token), ensure_ascii=True)+"$").encode('ascii'))
            return True
        except:
            return False

    def is_alive(self):
        try:
            self.write_noclose((json.dumps(self.get_request(AlarmAction.STATUS, self.token), ensure_ascii=True)+"$").encode('ascii'))
            response = json.loads(self.read_all().decode('ascii'))
            self.close()
            return response is not None and response['status'] == 'OK'
        except:
            return False

    def register_status(self):
        message = 'OK CONNECTION'
        error_code = 0
        is_alive = self.is_alive()
        if not is_alive:
            message = 'ERROR CONNECTION'
            error_code = 1
        AbstractSQL.execute_commit(self.get_insert_query(), (self.name, message, error_code))
        return is_alive

    def open_safe(self):
        try:
            if not self.is_open:
                self.open(self.host, self.port)
                self.is_open = True
        except:
            self.is_open = False
            AbstractSQL.execute_commit(self.get_insert_query(), (self.name, 'ERROR CONNECTION', 1))
            raise ConnectionError('No connection')

    def write_noclose(self, buffer):
        self.open_safe()
        super().write(buffer)

    def write(self, buffer):
        self.write_noclose(buffer)
        self.close()

    def close(self):
        self.is_open = False
        super().close()

    # actually there's only one alarm.
    def set_alarms(self, status):
        if status != TypeAlarmAction.NOTHING:
            what_to_do = AlarmAction.DEACTIVATE
            if status == TypeAlarmAction.ACTIVATE:
                what_to_do = AlarmAction.ACTIVATE
            elif status == TypeAlarmAction.DEACTIVATE:
                what_to_do = AlarmAction.DEACTIVATE
            return self.send_what_to_do(what_to_do)
        return False

    @staticmethod
    def get_info_alarm(name):
        query = AbstractSQL.get_query_by_name('GET_INFO_ALARM')
        row = AbstractSQL.fetch_execute_one(query, (name,))
        return row[0], row[1], row[2]

    @staticmethod
    def get_insert_query():
        return AbstractSQL.get_query_by_name('LOG_STATUS_REGISTER_ALARM')

    @staticmethod
    def get_all_alarms():
        query = AbstractSQL.get_query_by_name('GET_ALL_INFO_ALARMS')
        rows = AbstractSQL.fetch_execute_all(query, ())
        return rows

    @staticmethod
    def get_request(action, token):
        return {
            'token' : token,
            'action' : int(action)
        }
