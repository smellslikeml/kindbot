#!/usr/bin/python2
import sys
import sqlite3
sys.path.append('/home/pi/kindbot/')
sys.path.append('/home/pi/kindbot/utils/')
from utils import vpd_lin_trans, on_off

from datetime import datetime, timedelta


if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read('/home/pi/kindbot/config.ini')
    dev_idx = sys.argv[1]
    duration = sys.argv[2]
    while True:
        conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
        c = conn.cursor()
        res = c.execute("""select * from environ order by rowid desc limit 1;""")
        c.close()
        dt, T, H, vpd = res.fetchone()
        min_delay = vpd_lin_trans(vpd)
        on_off(dev_idx, duration)
        sleep(60 * min_delay)
