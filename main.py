#!/usr/bin/env python3.5
from module.SpmMain import SpmMain
from module.SpmSerial import SpmSerial
from module.SpmAlarm import SpmAlarm
from module.SpmUpdateAccessCode import SpmUpdateAccessCode
import sys

def main():
    SpmMain().start()
    SpmUpdateAccessCode().start()
    if not (len(sys.argv) > 1 and sys.argv[1] == '-develop'):
        SpmSerial().start()
        SpmAlarm().start()

if __name__ == "__main__":
    main()