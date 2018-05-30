#!/usr/bin/env python3.5
from module.SpmMain import SpmMain
from module.SpmSerial import SpmSerial
from module.SpmAlarm import SpmAlarm
from module.SpmSocketJSON import SpmSocketJSON

SpmMain().start()
SpmSerial().start()
SpmAlarm().start()
SpmSocketJSON().start()