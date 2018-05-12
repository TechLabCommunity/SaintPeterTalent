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
        AbstractSQL.execute_commit(query, (talent_code, member_type, int(is_enter), int(alarm_activation)))
        return True

    @staticmethod
    def empty_jail():
        query = AbstractSQL.get_query_by_name('TRUNCATE_ONLINE_MEMBERS')
        AbstractSQL.execute_commit(query, ())
        return True

