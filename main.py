import glob
import serial
from enum import Enum
from lib.SPControl import SPControl,TypeAlarmAction
from lib.AlarmNotification import AlarmNotification, AlarmAction

class TypeResult(Enum):
    OKCODE = b'a',
    NOCODE = b'c',
    OKCODEBSW = b'b'

#function to find first arduino's first usb port.
def find_usb_wiegand():
    usbports = glob.glob("/dev/ttyUSB*")
    if len(usbports) > 0:
        port = usbports[0]
    else:
        return None, False
    return port, True

#actually there's only one alarm.
def set_alarms(status):
    if status != TypeAlarmAction.NOTHING:
        what_to_do = AlarmAction.DEACTIVATE
        alarm_connection = AlarmNotification('ALARM_TL')
        if status == TypeAlarmAction.ACTIVATE:
            what_to_do = AlarmAction.ACTIVATE
            print('Activate alarm')
        elif status == TypeAlarmAction.DEACTIVATE:
            what_to_do = AlarmAction.DEACTIVATE
            print('Deactivate alarm')
        res_alarm = alarm_connection.send_what_to_do(what_to_do)
        print(res_alarm)

wiegand_port = find_usb_wiegand()
while True:
    try:
        with serial.Serial(wiegand_port, 9600) as wiegand:
            x = wiegand.readline().strip().decode('utf-8')
        code = ''
        if x:
            part = x.partition('#')
            if len(part) > 0:
                code = part[0]
                print(code)
                system_alarm = SPControl()
                _, _, talent_code, _, _, is_good, _, alarm_status, __ = system_alarm.enter_code(code)
                char_send = TypeResult.OKCODEBSW.value
                print(TypeResult.OKCODEBSW.value)
                if talent_code is not None:
                    if is_good:
                        char_send = TypeResult.OKCODE.value[0]
                    else:
                        char_send = TypeResult.NOCODE.value[0]
                with serial.Serial(wiegand_port, 9600) as wiegand:
                    wiegand.write(char_send)
                try:
                    set_alarms(alarm_status)
                except:
                    print("res alarm no connection")
    except:
        found_usb = False
        while not found_usb:
            wiegand_port, found_usb = find_usb_wiegand()
        print(wiegand_port)
        pass