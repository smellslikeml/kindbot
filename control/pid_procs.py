#!/usr/bin/env python
import sys
import socket
import sqlite3
from time import sleep
from datetime import datetime
sys.path.append('/home/pi/kindbot/')
sys.path.append('/home/pi/kindbot/utils/')
from utils import day_time

class pid_controller():
    """Calculate System Input using a PID Controller

    Arguments:
    y  .. Measured Output of the System
    yc .. Desired Output of the System
    h  .. Sampling Time
    Kp .. Controller Gain Constant
    Ki .. Controller Integration Constant
    Kd .. Controller Derivation Constant
    u0 .. Initial state of the integrator
    e0 .. Initial error

    Make sure this function gets called every h seconds!
    """

    def __init__(self, ui_prev=0.1, e_prev=0):
        self.ui_prev = ui_prev
        self.e_prev = e_prev
        self.h = 180
        self.Ki = 0.001
        self.Kd = 0.001
        self.Kp = 0.001
        self.u0 = 0
        self.e0 = 0
        self.thresh = -7

    def pid_step(self, y, yc):
        # Error
        e = yc - y
        # Integration Input
        ui = self.ui_prev + self.h * self.e
        # Derivation Input
        ud = (e - self.e_prev) / self.h

        # update values
        self.e_prev = e
        self.ui_prev = ui

        # Calculate input for the system
        u = self.Kp * e + self.Ki * ui + self.Kd * ud
        if u < self.thresh:
            comm = 'on'
        else:
            comm = 'off'
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", 9000))
            data = DEV_IDX + " " + comm
            sock.sendall(data.encode())
            result = sock.recv(1024).decode()
            sock.close()
        except:
            sock.close()
        return comm, u


if __name__ == '__main__':
    import configparser
    DEV_IDX = sys.argv[1]

    config = configparser.ConfigParser()
    config.read('/home/pi/kindbot/config.ini')
    setpoint = float(config['DAYTIME']['SETPOINT'])

    pc = pid_controller()
    
    while True:
        if day_time():
            conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
            c = conn.cursor()
            res = c.execute("""select * from environ order by rowid desc limit 1;""")
            dt, temp, hum, vpd_val = res.fetchone()
            comm, output = pc.pid_step(temp, setpoint)
            tm_stp = str(datetime.now())
            lmt = h if comm == 'off' else min((-60 * output, 1800))
            c.execute("""insert into environ values (?, ?, ?, ?, ?, ?, ?, ?)""", (tm_stp, temp, hum, output, vpd_val, ui_prev, e_prev, comm))
            conn.commit()
            c.close()
            sleep(lmt)



