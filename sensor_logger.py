#!/usr/bin/python2
from subprocess import Popen

while True:
    p = Popen('/home/pi/kindbot/sensor.py', shell=True)
    p.wait()
