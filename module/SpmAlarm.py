from threading import Thread
from lib.SPControl import TypeAlarmAction
from lib.SPDbCall import SPDbCall
from lib.AlarmNotification import AlarmNotification
from time import sleep

class SpmAlarm(Thread):

    NAMEMODULE = "Alarm"

    def __init__(self):
        print(self.NAMEMODULE)
        Thread.__init__(self)

    def run(self):
        while True:
            id, name_alarm, alarm_action = SPDbCall.get_next_alarm_request()
            if id is not None and alarm_action is not TypeAlarmAction.NOTHING:
                try:
                    SPDbCall.set_alarm_request_done(id)
                    AlarmNotification(name_alarm).set_alarms(alarm_action)
                except:
                    pass
            sleep(0.1)