import unittest
from lib.AlarmNotification import AlarmNotification, AlarmAction


class AlarmNotificationTest(unittest.TestCase):

    def test_is_active_alarm(self):
        for alarm in AlarmNotification.get_all_alarms():
            #select by name
            test = AlarmNotification(alarm[0])
            self.assertTrue(test.register_status())

    def test_random_call(self):
        for alarm in AlarmNotification.get_all_alarms():
            #select by name
            test = AlarmNotification(alarm[0])
            for e in AlarmAction:
                self.assertTrue(test.send_what_to_do(e))


if __name__ == '__main__':
    unittest.main()
