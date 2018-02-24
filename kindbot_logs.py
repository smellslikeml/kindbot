#!/usr/bin/env python
'''
From https://www.blog.pythonlibrary.org/2014/02/11/python-how-to-create-rotating-logs/
'''
import logging
import time
import sys
from datetime import datetime
 
from logging.handlers import RotatingFileHandler

sys.path.append('/home/pi/DHT11_Python/')
import RPi.GPIO as GPIO
import dht11

sys.path.append('/home/pi/tsl2561/')
from tentacle_pi.TSL2561 import TSL2561

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

tsl = TSL2561(0x39,"/dev/i2c-1")
tsl.enable_autogain()
tsl.set_time(0x00)

def lux_reading():
    return tsl.lux()

instance = dht11.DHT11(pin = 4)
 
#----------------------------------------------------------------------
def create_rotating_log(path):
    """
    Creates a rotating log
    """
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
 
    # add a rotating handler
    handler = RotatingFileHandler(path, maxBytes=20,
                                  backupCount=5)
    logger.addHandler(handler)
 
    while True:
        result = instance.read()
        if result.is_valid():
            tm_stmp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            temp = 32 + (9 / 5) * result.temperature
            humidity = result.humidity
	    lux = lux_reading()
	    logger.info("Time: {}, Humidity: {}, Temperature: {}, Lumens: {}".format(tm_stmp, humidity, temp, lux))
	    time.sleep(120)
        else:
            pass
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    log_file = "/home/pi/kindbot/app/kindbot.log"
    create_rotating_log(log_file)
