#!/usr/bin/env python3.5
import glob
import serial
from enum import Enum
from lib.SPControl import SPControl, TypeEnter
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
    logger = AccessLogger('./log/log.txt')
    while True:
        id, code = SPDbCall.get_next_request()
        if id is not None:
            SPDbCall.set_request_done(id)
            system_access = SPControl()
            name, surname, talent_code, _, _, is_good, type_enter, alarm_status, __ = system_access.enter_code(code)
            char_send = TypeResult.NOCODE.value[0]
            if talent_code is not None:
                if is_good:
                    if type_enter == TypeEnter.ENTER:
                        char_send = TypeResult.OKCODEENTER.value[0]
                    else:
                        char_send = TypeResult.OKCODEEXIT.value[0]
                else:
                    char_send = TypeResult.OKCODEBSW.value
                logger.log('%s, %s, %s, %s' % (name, surname, talent_code, type_enter))
            SPDbCall.insert_request_serial(char_send)
            try:
                AlarmNotification('ALARM_TL').set_alarms(alarm_status)
                logger.log('Alarm Status : %s' % (alarm_status))
            except:
                logger.log('Alarm Status NOT WORKING')
                pass
        sleep(0.1)

main_thread = threading.Thread(target=launch_main)
main_thread.start()
serial_thread = threading.Thread(target=launch_serial)
serial_thread.start()