#!/usr/bin/env python
import time
from pyHS100 import Discover

for dev in Discover.discover().values():
    print(dev)

dev.turn_off()
for i in range(5):
    dev.turn_on()
    time.sleep(10)
    dev.turn_off()
    time.sleep(5)

