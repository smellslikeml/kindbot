#!/usr/bin/env python
'''
From https://www.blog.pythonlibrary.org/2014/02/11/python-how-to-create-rotating-logs/
'''
import logging
import time
import sys
from datetime import datetime
import smbus
 
from logging.handlers import RotatingFileHandler

import RPi.GPIO as GPIO

#sys.path.append('/home/pi/tsl2561/')
#from tentacle_pi.TSL2561 import TSL2561

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

#tsl = TSL2561(0x39,"/dev/i2c-1")
#tsl.enable_autogain()
#tsl.set_time(0x00)

def lux_reading():
    return tsl.lux()



#### New Humid + Temp sensor ######
bus = smbus.SMBus(1)

def get_humid():
    bus.write_byte(0x40, 0xF5)
    time.sleep(0.3)
    data0 = bus.read_byte(0x40)
    data1 = bus.read_byte(0x40)
    humidity = ((data0 * 256 + data1) * 125 / 65536.0) - 6
    return humidity

def get_temp():
    bus.write_byte(0x40, 0xF3)
    time.sleep(0.3)
    data0 = bus.read_byte(0x40)
    data1 = bus.read_byte(0x40)
    cTemp = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85
    fTemp = cTemp * 1.8 + 32
    return fTemp

#----------------------------------------------------------------------
def create_rotating_log(path):
    """
    Creates a rotating log
    """
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
 
    # add a rotating handler
    handler = RotatingFileHandler(path, maxBytes=20,
                                  backupCount=24)
    logger.addHandler(handler)
 
    while True:
        try:
            tm_stmp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            humidity = get_humid()
            time.sleep(0.3)
            temp = get_temp()
	        #lux = lux_reading()
	        dict_str = {'Time':tm_stmp, 'Humidity':humidity, 'Temperature':temp } #, 'Lumens':lux}
            dict_str = str(dict_str)
            print dict_str
	    logger.info(dict_str)
	    time.sleep(3600)
        except:
            pass
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    log_file = "/home/pi/kindbot/app/logs/kindbot.log"
    create_rotating_log(log_file)
