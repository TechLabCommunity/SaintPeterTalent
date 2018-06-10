from enum import IntEnum
from lib.AbstractSQL import AbstractSQL

class TypeEnter(IntEnum):
    NOTHING = 0,
    ENTER = 1,
    EXIT = 2

class TypeAlarmAction(IntEnum):
    NOTHING = 0,
    ACTIVATE = 1,
    DEACTIVATE = 2

class SPDbCall:

    @staticmethod
    def exists_access_code(access_code):
        query = AbstractSQL.get_query_by_name('EXISTS_ACCESS_CODE')
        return AbstractSQL.fetch_execute_one(query, (access_code,))

    # (talent_code, member_type, is_master)
    @staticmethod
    def get_info_user(access_code):
        if access_code is None or not access_code:
            return None, None, None, None, None
        query = AbstractSQL.get_query_by_name('INFO_USER_ACCESS')
        row = AbstractSQL.fetch_execute_one(query, (access_code,))
        if row is None:
            return None, None, None, None, None
        return row[0], row[1], row[2], row[3], list(map(int, row[4].split(',')))

    @staticmethod
    def is_online(talent_code):
        if talent_code is None or not talent_code:
            return False
        query = AbstractSQL.get_query_by_name('IS_ONLINE_USER')
        row = AbstractSQL.fetch_execute_one(query, (talent_code,))
        return row is not None

    @staticmethod
    def n_user_online():
        query = AbstractSQL.get_query_by_name('N_USER_ONLINE')
        row = AbstractSQL.fetch_execute_one(query, ())
        return int(row[0])

    @staticmethod
    def n_type_user(member_type):
        if member_type is None or len(member_type) == 0:
            return 0
        query = AbstractSQL.get_query_by_name('N_TYPE_USER')
        row = AbstractSQL.fetch_execute_one(query, (','.join(list(map(str, member_type))),))
        return int(row[0])

    @staticmethod
    def exit_user(talent_code):
        if talent_code is None or not talent_code:
            return False
        if not SPDbCall.is_online(talent_code):
            return False
        query = AbstractSQL.get_query_by_name('EXIT_USER')
        AbstractSQL.execute_commit(query, (talent_code,))
        return True

    @staticmethod
    def enter_user(talent_code, member_type):
        if talent_code is None or not talent_code or member_type is None:
            return False
        if SPDbCall.is_online(talent_code):
            return False
        query = AbstractSQL.get_query_by_name('ENTER_USER')
        AbstractSQL.execute_commit(query, (talent_code,member_type))
        return True

    @staticmethod
    def all_dependent_by(member_type):
        if member_type is None:
            return None
        query = AbstractSQL.get_query_by_name('LIST_MEMBER_DEPENDING').format(str(member_type))
        rows = AbstractSQL.fetch_execute_all(query, ())
        ids = []
        for r in rows:
            ids.append(r[0])
        return ids

    @staticmethod
    def save_log(talent_code, member_type, is_enter, alarm_activation):
        if talent_code is None or member_type is None:
            return False
        query = AbstractSQL.get_query_by_name('SAVE_LOG')
        if alarm_activation is None:
            alarm_activation = TypeAlarmAction.NOTHING
        AbstractSQL.execute_commit(query, (talent_code, member_type, int(is_enter), int(alarm_activation)))
        return True

    @staticmethod
    def empty_jail():
        query = AbstractSQL.get_query_by_name('TRUNCATE_ONLINE_MEMBERS')
        AbstractSQL.execute_commit(query, ())
        return True

    @staticmethod
    def insert_request_access(accesscode):
        if not accesscode or accesscode is None:
            return False
        query = AbstractSQL.get_query_by_name('INSERT_REQUEST_ACCESS')
        AbstractSQL.execute_commit(query, (accesscode,))
        return True

    @staticmethod
    def get_next_request():
        query = AbstractSQL.get_query_by_name('GET_NEXT_REQUEST_ACCESS')
        row = AbstractSQL.fetch_execute_one(query, ())
        if row is None:
            return None, None
        return int(row[0]), str(row[1])

    @staticmethod
    def set_request_done(id):
        query = AbstractSQL.get_query_by_name('SET_REQUEST_DONE')
        try:
            AbstractSQL.execute_commit(query, (int(id),))
            return True
        except:
            return False

    @staticmethod
    def insert_request_serial(stringtosend):
        if not stringtosend or stringtosend is None:
            return False
        query = AbstractSQL.get_query_by_name('INSERT_REQUEST_SERIAL')
        AbstractSQL.execute_commit(query, (stringtosend,))
        return True

    @staticmethod
    def get_next_serial_request():
        query = AbstractSQL.get_query_by_name('GET_NEXT_STRINGTOSEND')
        row = AbstractSQL.fetch_execute_one(query, ())
        if row is None:
            return None, None
        return int(row[0]), str(row[1])

    @staticmethod
    def set_serial_request_done(id):
        query = AbstractSQL.get_query_by_name('SET_REQUEST_SERIAL_DONE')
        try:
            AbstractSQL.execute_commit(query, (int(id),))
            return True
        except:
            return False

    @staticmethod
    def insert_request_alarm(alarm_name, alarm_action):
        if alarm_name is None or not alarm_name:
            return False
        query = AbstractSQL.get_query_by_name('INSERT_ALARM_REQUEST')
        AbstractSQL.execute_commit(query, (int(alarm_action),alarm_name))
        return True

    @staticmethod
    def get_next_alarm_request():
        query = AbstractSQL.get_query_by_name('GET_NEXT_ALARM_REQUEST')
        row = AbstractSQL.fetch_execute_one(query, ())
        if row is None:
            return None, None, None
        return int(row[0]), str(row[1]), TypeAlarmAction(int(row[2]))

    @staticmethod
    def set_alarm_request_done(id):
        query = AbstractSQL.get_query_by_name('SET_ALARM_REQUEST_DONE')
        try:
            AbstractSQL.execute_commit(query, (int(id),))
            return True
        except:
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
    def insert_member(table_name, member):
        if table_name is None or member is None:
            return False
        query = AbstractSQL.get_query_by_name('INSERT_MEMBER_TABLE').replace('table_name', table_name)
        AbstractSQL.execute_commit(query,
                                   (
                                    member['Name'],
                                    member['Surname'],
                                    member['MemberType'],
                                    member['ReferenceZone'],
                                    member['AccessCode'],
                                    member['IsActive'],
                                    member['TalentCode'],
                                    member['Username'],
                                    member['Password'],
                                    member['FirstEmail'],
                                    member['FiscalCode']
                                    )
                                   )
        return True

    @staticmethod
    def update_accesscode(table_name, access_code, talent_code):
        if table_name is None or talent_code is None or access_code is None:
            return False
        query = AbstractSQL.get_query_by_name('UPDATE_ACCESSCODE').replace('table_name', table_name)
        AbstractSQL.execute_commit(query, (access_code, talent_code))
        return True

    @staticmethod
    def exists_talent_code(talent_code):
        query = AbstractSQL.get_query_by_name('EXISTS_TALENTCODE')
        return AbstractSQL.fetch_execute_one(query, (talent_code,))

