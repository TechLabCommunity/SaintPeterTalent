#!/usr/bin/env python3.5
import glob
import serial
from enum import Enum
from lib.SPControl import SPControl, TypeEnter, TypeAlarmAction
from lib.AlarmNotification import AlarmNotification
from lib.AccessLogger import AccessLogger
from time import sleep
import threading
from lib.SPDbCall import SPDbCall

class TypeResult(Enum):
    OKCODEENTER = b's',
    OKCODEEXIT = b'a',
    NOCODE = b'b',
    OKCODEBSW = b'c'

PATH_LOG = './log/log.txt'

def get_wiegand_serial():
    was_found = False
    w_port = None
    w_serial = None
    #inner function
    def find_usb_wiegand():
        usbports = glob.glob("/dev/ttyUSB*")
        if len(usbports) > 0:
            port = usbports[0]
        else:
            return None, False
        return port, True
    while not w_serial:
        try:
            while not was_found:
                    w_port, was_found = find_usb_wiegand()
            w_serial = serial.Serial(w_port, 9600, timeout=0.2)
        except:
            pass
    return w_serial

def launch_alarm():
    while True:
        id, name_alarm, alarm_action = SPDbCall.get_next_alarm_request()
        if id is not None and alarm_action is not TypeAlarmAction.NOTHING:
            try:
                SPDbCall.set_alarm_request_done(id)
                AlarmNotification(name_alarm).set_alarms(alarm_action)
            except:
                pass
        sleep(0.1)

def launch_serial():
    wiegand_serial = get_wiegand_serial()
    while True:
        try:
            x = wiegand_serial.readline().strip().decode('utf-8')
            if x:
                part = x.partition('#')
                if len(part) > 0:
                    code = part[0]
                    SPDbCall.insert_request_access(code)
            id, stos = SPDbCall.get_next_serial_request()
            if id is not None:
                SPDbCall.set_serial_request_done(id)
                wiegand_serial.write(str.encode(stos))
        except:
            sleep(3)
            wiegand_serial = get_wiegand_serial()
            pass


def launch_main():
    logger = AccessLogger(PATH_LOG)
    while True:
        try:
            id, code = SPDbCall.get_next_request()
            if id is not None:
                SPDbCall.set_request_done(id)
                system_access = SPControl()
                name, surname, talent_code, member_type, _, is_good, type_enter, alarm_status, __ = system_access.enter_code(code)
                if talent_code is not None:
                    logger.log('%s, %s, %s, %s, %s' % (name, surname, talent_code, type_enter, code))
                    if is_good:
                        if type_enter == TypeEnter.ENTER:
                            char_send = TypeResult.OKCODEENTER.value[0]
                        else:
                            char_send = TypeResult.OKCODEEXIT.value[0]
                    else:
                        char_send = TypeResult.OKCODEBSW.value
                        logger.log('Code valid but there is anomaly : ' + str(member_type))
                    SPDbCall.insert_request_serial(char_send)
                    logger.log('Alarm action : '+str(alarm_status))
                    if alarm_status is not TypeAlarmAction.NOTHING:
                        for al in SPDbCall.get_all_alarms():
                            SPDbCall.insert_request_alarm(str(al[0]), alarm_status)
            sleep(0.1)
        except Exception as e:
            logger.log("Exception : "+str(e))

main_thread = threading.Thread(target=launch_main)
serial_thread = threading.Thread(target=launch_serial)
alarm_thread = threading.Thread(target=launch_alarm)
serial_thread.start()
main_thread.start()
alarm_thread.start()
