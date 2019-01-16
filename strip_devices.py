#!/usr/bin/python3
import os
import sys
import time
import socket
import sqlite3
from datetime import datetime
sys.path.append(os.environ['HOME'] + '/pyHS100')
sys.path.append('/home/pi/kindbot/')
from pyHS100 import SmartStrip, SmartDeviceException


class smartstrip():
    def __init__(self, logging=None, strip=None):
        self.logging = logging
        self.ip = None
        if strip is None:
            self.strip = self.get_smart_strip()
        else:
            self.strip = strip

    def get_smart_strip(self, max_ip=200):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        loc = '.'.join(ip.split('.')[:-1])

        idx = 0
        while True:
            if idx > max_ip:
                break
            try:
                strip = SmartStrip('{}.{}'.format(loc, idx))
                return strip
            except SmartDeviceException:
                idx += 1
                pass  
        return 

    def dev_comm(self, command, dev_idx):
        if self.strip is not None:
            plg = self.strip.plugs[dev_idx]
            if command == 'on':
                plg.turn_on()
            elif command == 'off':
                duration = round((plg.time - plg.on_since).total_seconds(), 2)
                self.sess_watts = round(duration / 3600 * plg.current_consumption(), 2)
                plg.turn_off()
                dt = str(datetime.now()).split('.')[0]
                if self.logging:
                    conn = sqlite3.connect(self.logging, timeout=30000)
                    c = conn.cursor()
                    c.execute("""insert into devices values (?, ?, ?, ?)""", (dt, dev_idx, duration, self.sess_watts))
                    conn.commit()
                    c.close()
        else:
            self.get_smart_strip()
            time.sleep(3)
            self.dev_comm(command, dev_idx)


if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read('/home/pi/kindbot/config.ini')
    dev_idx = int(sys.argv[1])
    comm = sys.argv[2]
    strip = smartstrip(logging=config['PATHS']['DB_PATH'])
    strip.dev_comm(comm, dev_idx)

