import unittest
from lib.SPControl import SPControl
from lib.AbstractSQL import AbstractSQL
from lib.SPDbCall import TypeEnter
from lib.SPDbCall import TypeAlarmAction
import xml.etree.ElementTree as ET

class SPControlTest(unittest.TestCase):

    s = SPControl()

    QUERY_CODE_STANDARD = "SELECT AccessCode from talent_members A inner join type_members B on (A.MemberType = B.ID and B.DependingOn != '-1') WHERE AccessCode not in (%s) order by rand() limit 1 "
    QUERY_CODE__DEPENDING_MASTER = "SELECT A.AccessCode from talent_members A"\
        " WHERE A.AccessCode not in (%s) and exists("\
        " select 1 from talent_members C inner join type_members B on (C.MemberType = B.ID and B.DependingOn != '-1')"\
        " where C.AccessCode = %s and (B.DependingOn = A.MemberType OR B.DependingOn like concat(A.MemberType,',%%') or B.DependingOn like concat('%%,', A.MemberType) or B.DependingOn like CONCAT('%%,', A.MemberType, ',%%')))"\
        " order by rand() limit 1"
    QUERY_CODE_MASTER = "SELECT AccessCode from talent_members A inner join type_members B on (A.MemberType = B.ID and B.DependingOn = '-1') WHERE AccessCode not in (%s) order by rand() limit 1 "

    @staticmethod
    def resetDB():
        AbstractSQL.execute_commit("TRUNCATE online_accesses", ())
        AbstractSQL.execute_commit("TRUNCATE log_accesses", ())

    def test_invalid_access_code(self):
        for codex in ['', 'A', '---']:
            self.assertIsNone(self.s.enter_code(codex)[0])

    def test_invalid_access_first_standard(self):
        self.resetDB()
        access_code_standard = AbstractSQL.fetch_execute_one(self.QUERY_CODE_STANDARD, ('-1',))[0]
        _, _, talent_code, member_type, _, result, type_enter, alarm_action, _ = self.s.enter_code(access_code_standard)
        self.assertFalse(result)
        self.assertEqual(type_enter, TypeEnter.ENTER)
        self.assertEqual(alarm_action, TypeAlarmAction.NOTHING)
        self.resetDB()

    def test_valid_access_first_master(self):
        self.resetDB()
        access_code_master = AbstractSQL.fetch_execute_one(self.QUERY_CODE_MASTER, ('-1',))[0]
        _, _, talent_code, member_type, _, result, type_enter, alarm_action, _ = self.s.enter_code(access_code_master)
        self.assertTrue(result)
        self.assertEqual(type_enter, TypeEnter.ENTER)
        self.assertEqual(alarm_action, TypeAlarmAction.DEACTIVATE)
        self.resetDB()

    def test_valid_access_depending(self):
        self.resetDB()
        access_code_standard = AbstractSQL.fetch_execute_one(self.QUERY_CODE_STANDARD, ('-1',))[0]
        access_code_master_depending = AbstractSQL.fetch_execute_one(self.QUERY_CODE__DEPENDING_MASTER, ('-1', access_code_standard))[0]
        _, _, talent_code, member_type, _, result, type_enter, alarm_action, _ = self.s.enter_code(access_code_master_depending)
        self.assertTrue(result)
        self.assertEqual(type_enter, TypeEnter.ENTER)
        self.assertEqual(alarm_action, TypeAlarmAction.DEACTIVATE)
        _, _, talent_code, member_type, _, result, type_enter, alarm_action, _ = self.s.enter_code(access_code_standard)
        self.assertTrue(result)
        self.assertEqual(type_enter, TypeEnter.ENTER)
        self.assertEqual(alarm_action, TypeAlarmAction.NOTHING)
        self.s.enter_code(access_code_standard)
        _, _, talent_code, member_type, _, result, type_enter, alarm_action, _ = self.s.enter_code(access_code_master_depending)
        self.assertTrue(result)
        self.assertEqual(type_enter, TypeEnter.EXIT)
        self.assertEqual(alarm_action, TypeAlarmAction.ACTIVATE)
        self.resetDB()

    def test_valid_access_depending_2(self):
        self.resetDB()
        access_code_standard = AbstractSQL.fetch_execute_one(self.QUERY_CODE_STANDARD, ('-1',))[0]
        access_code_master_depending = AbstractSQL.fetch_execute_one(self.QUERY_CODE__DEPENDING_MASTER, ('-1', access_code_standard))[0]
        access_code_master_depending_2 = AbstractSQL.fetch_execute_one(self.QUERY_CODE__DEPENDING_MASTER, (access_code_master_depending, access_code_standard))[0]
        self.s.enter_code(access_code_master_depending)
        self.s.enter_code(access_code_master_depending_2)
        self.s.enter_code(access_code_standard)
        _, _, talent_code, member_type, _, result, type_enter, alarm_action, _ = self.s.enter_code(access_code_master_depending)
        self.assertTrue(result)
        self.assertEqual(type_enter, TypeEnter.EXIT)
        self.assertEqual(alarm_action, TypeAlarmAction.NOTHING)
        self.resetDB()

    def empty_jail(self):
        self.resetDB()
        code_jail = ET.parse(SPControl.PATH_CONFIG).getroot()[1].find('code').text
        _, _, talent_code, member_type, _, result, type_enter, alarm_action, _ = self.s.enter_code(code_jail)
        self.assertTrue(result)
        self.assertEqual(type_enter, TypeEnter.EXIT)
        self.assertEqual(alarm_action, TypeAlarmAction.ACTIVATE)
        self.resetDB()


if __name__ == '__main__':
    unittest.main()
