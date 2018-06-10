#!/usr/bin/env python3.5
from module.SpmMain import SpmMain
from module.SpmSerial import SpmSerial
from module.SpmAlarm import SpmAlarm
from module.SpmUpdateAccessCode import SpmUpdateAccessCode

SpmMain().start()
SpmSerial().start()
SpmAlarm().start()
SpmUpdateAccessCode().start()