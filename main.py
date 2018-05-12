import glob
import serial
from enum import Enum
from lib.SPControl import SPControl,TypeAlarmAction, TypeEnter
from lib.AlarmNotification import AlarmNotification, AlarmAction
from lib.AccessLogger import AccessLogger
from time import sleep
import threading

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

#todo get all alarms with status.
def launch_status_alarm():
    threading.Timer(5.0, launch_status_alarm).start()
    try:
        AlarmNotification('ALARM_TL').register_status()
    except:
        pass

def launch_sp():
    app_log = AccessLogger('./log/log.txt')
    wiegand_serial = get_wiegand_serial()
    while True:
        try:
            x = wiegand_serial.readline().strip().decode('utf-8')
            code = ''
            if x:
                part = x.partition('#')
                if len(part) > 0:
                    app_log.log('CREATE STREAM')
                    code = part[0]
                    app_log.log("Insert code : "+code)
                    system_alarm = SPControl()
                    name, surname, talent_code, _, _, is_good, type_enter, alarm_status, __ = system_alarm.enter_code(code)
                    app_log.log('Access member : %(talent_code)s, %(name)s, %(surname)s' % {'talent_code' : str(talent_code), 'name' : str(name), 'surname' : str(surname)})
                    char_send = TypeResult.NOCODE.value[0]
                    if talent_code is not None:
                        if is_good:
                            if type_enter == TypeEnter.ENTER:
                                app_log.log('Enter Mode')
                                char_send = TypeResult.OKCODEENTER.value[0]
                            else:
                                app_log.log('Exit Mode')
                                char_send = TypeResult.OKCODEEXIT.value[0]
                        else:
                            app_log.log('Code Valid but there\'s anomaly')
                            char_send = TypeResult.OKCODEBSW.value
                    else:
                        app_log.log('No code valid')
                    wiegand_serial.write(char_send)
                    try:
                        AlarmNotification('ALARM_TL').set_alarms(alarm_status)
                        app_log.log(str(alarm_status))
                    except:
                        app_log.log('ALARM NOT WORKING')
                    app_log.log('END STREAM')
        except:
            app_log.log("Serial failed.")
            sleep(3)
            wiegand_serial = get_wiegand_serial()
            pass

main_thread = threading.Thread(target=launch_sp)
main_thread.start()
launch_status_alarm()