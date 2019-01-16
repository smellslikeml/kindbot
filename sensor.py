#!/usr/bin/env python
import sys
import time
from time import strftime
import sqlite3
from datetime import datetime
from Adafruit_BME280 import *
import numpy as np
import smbus
import configparser
 
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

def get_temp(T_OFFSET=10):
    return 9 * (sensor.read_temperature() - T_OFFSET) / 5 + 32

def get_humid(H_OFFSET=-10):
    return sensor.read_humidity() - H_OFFSET

def get_vpd(T, H):
    A = -1.044e4
    B = -11.29
    C = -2.7e-2
    D = 1.289e-5
    E = -2.478e-9
    F = 6.456
    
    T += 459.67
    kpa_c = 6.89475729 
    vp = np.exp(A/T + B + C*T + D*T**2 + E*T**3 + F*np.log(T)) * (1 - H / 100)
    vp *= kpa_c 
    return vp

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/home/pi/kindbot/config.ini')
    T_OFFSET = int(config['DAYTIME']['T_OFFSET'])
    H_OFFSET = int(config['DAYTIME']['H_OFFSET'])
    S_INTERVAL = int(config['DAYTIME']['S_INTERVAL'])

    T = get_temp(T_OFFSET=T_OFFSET)
    H = get_humid(H_OFFSET=H_OFFSET)
    VPD = get_vpd(T, H)

    conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
    c = conn.cursor()
    c.execute("""insert into environ values (?, ?, ?, ?)""", (str(datetime.now()).split('.')[0], round(T, 2), round(H, 2), round(VPD, 2)))
    conn.commit()
    c.close()

    time.sleep(S_INTERVAL)

