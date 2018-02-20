#!/usr/bin/env python
import os
import sys
import time
from datetime import datetime


sys.path.append('/home/pi/DHT11_Python/')
import RPi.GPIO as GPIO
import dht11

sys.path.append('/home/pi/tsl2561/')
from tentacle_pi.TSL2561 import TSL2561

#from email_sender import send_email
#from sms_sender import *

import BaseHTTPServer
import json
from BaseHTTPServer import BaseHTTPRequestHandler

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()


tsl = TSL2561(0x39,"/dev/i2c-1")
tsl.enable_autogain()
tsl.set_time(0x00)

def lux_reading():
    return tsl.lux()

def hi_low():
    GPIO.setup(17, GPIO.IN)
    return GPIO.input(17)

# read data using pin 14
instance = dht11.DHT11(pin = 4)

log_file = <YOUR_HOME_DIRECTORY> + "kindbot/sensor_log.txt"

while True:
    tm_stmp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f_tmp = 32 + (9 / 5) * result.temperature
    hum = result.humidity
    if os.path.exists(log_file):
        with open(log_file, "a") as fl:
        fl.write('%s,%s,%s,%s\n'.format( str(tm_stmp), str(f_tmp), str(hum), str(lux_reading())) )
    else:
        with open(log_file, "wb") as fl:
        fl.write('%s,%s,%s,%s\n'.format( str(tm_stmp), str(f_tmp), str(hum), str(lux_reading())) )
    time.sleep(300)
