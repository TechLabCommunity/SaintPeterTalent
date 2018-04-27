import glob
import serial
from lib.SPControl import SPControl,TypeAlarmAction
from lib.AlarmNotification import AlarmNotification, AlarmAction

def find_usb_wiegand():
    usbports = glob.glob("/dev/ttyUSB*")
    if len(usbports) > 0:
        wiegand_port = usbports[0]
    else:
        return None, False
    print(wiegand_port)
    return wiegand_port, True

wiegand_port = find_usb_wiegand()
while True:
    try:
        with serial.Serial(wiegand_port, 9600) as ser:
            x = ser.readline().strip().decode('utf-8')
            code = ''
            if x:
                part = x.partition('#')
                if len(part) > 0:
                    code = part[0]
                    system_alarm = SPControl()
                    res = system_alarm.enter_code(code)
                    print(res)
                    alarm_status = res[7]
                    if alarm_status != TypeAlarmAction.NOTHING:
                        what_to_do = AlarmAction.DEACTIVATE
                        alarm_connection = AlarmNotification('ALARM_TL')
                        if alarm_status == TypeAlarmAction.ACTIVATE:
                            what_to_do = AlarmAction.ACTIVATE
                            print('Activate alarm')
                        elif alarm_status == TypeAlarmAction.DEACTIVATE:
                            what_to_do = AlarmAction.DEACTIVATE
                            print('Deactivate alarm')
                        res_alarm = alarm_connection.send_what_to_do(what_to_do)
                        print(res_alarm)
    except:
        found_usb = False
        while not found_usb:
            wiegand_port, found_usb = find_usb_wiegand()
        pass