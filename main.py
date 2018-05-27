#!/usr/bin/env python3.5
from module.SpmSerial import SpmSerial
from module.SpmMain import SpmMain
from module.SpmAlarm import SpmAlarm

def launch_sp():
    SpmMain().start()
    SpmSerial().start()
    SpmAlarm().start()

launch_sp()