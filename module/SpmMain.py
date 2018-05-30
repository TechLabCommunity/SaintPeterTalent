from threading import Thread
from enum import Enum
from lib.AccessLogger import AccessLogger
from lib.SPControl import SPControl, TypeEnter, TypeAlarmAction
from lib.SPDbCall import SPDbCall
from time import sleep

class TypeResult(Enum):
    OKCODEENTER = b's',
    OKCODEEXIT = b'a',
    NOCODE = b'b',
    OKCODEBSW = b'c'

class SpmMain(Thread):

    NAMEMODULE = "Main Process"

    PATH_LOG = './log/log.txt'

    def __init__(self):
        print(self.NAMEMODULE)
        Thread.__init__(self)

    def run(self):
        logger = AccessLogger(self.PATH_LOG)
        while True:
            try:
                id, code = SPDbCall.get_next_request()
                if id is not None:
                    SPDbCall.set_request_done(id)
                    system_access = SPControl()
                    name, surname, talent_code, member_type, _, is_good, type_enter, alarm_status, __ = system_access.enter_code(
                        code)
                    char_send = TypeResult.NOCODE
                    if talent_code is not None:
                        if is_good:
                            if type_enter == TypeEnter.ENTER:
                                char_send = TypeResult.OKCODEENTER.value[0]
                            else:
                                char_send = TypeResult.OKCODEEXIT.value[0]
                        else:
                            char_send = TypeResult.OKCODEBSW.value
                        logger.log('Alarm action : ' + str(alarm_status))
                        if alarm_status is not TypeAlarmAction.NOTHING:
                            for al in SPDbCall.get_all_alarms():
                                SPDbCall.insert_request_alarm(str(al[0]), alarm_status)
                        logger.log('Code valid but there is anomaly : ' + str(member_type))
                    logger.log('%s, %s, %s, %s, %s' % (name, surname, talent_code, type_enter, code))
                    SPDbCall.insert_request_serial(char_send)
                sleep(0.1)
            except Exception as e:
                logger.log("Exception : " + str(e))