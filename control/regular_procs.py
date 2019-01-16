#!/usr/bin/env python3
import sys
import sqlite3
import configparser
from time import sleep
sys.path.append('/home/pi/kindbot/utils/')
from utils import vpd_lin_trans, on_off

config = configparser.ConfigParser()
config.read('/home/pi/kindbot/config.ini')

def regular(dev_idx, duration, on_every):
    while True:
        on_off(dev_idx, duration)
        sleep(on_every)


if __name__ == "__main__":
    import sys
    dev_idx = sys.argv[1]
    duration = float(sys.argv[2])
    on_every = float(sys.argv[3])
    regular(dev_idx, duration, on_every)

