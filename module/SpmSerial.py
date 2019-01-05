from threading import Thread
import serial
import glob
from lib.SPDbCall import SPDbCall
from time import sleep

class SpmSerial(Thread):

    NAMEMODULE = "Serial"

    def __init__(self):
        print(self.NAMEMODULE)
        Thread.__init__(self)

    @staticmethod
    def get_wiegand_serial():
        was_found = False
        w_port = None
        w_serial = None

        # inner function
        def find_usb_wiegand():
            usbports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
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

    def run(self):
        wiegand_serial = self.get_wiegand_serial()
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
                wiegand_serial = self.get_wiegand_serial()
                pass
