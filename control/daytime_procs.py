#!/usr/bin/env python3
import sys
import socket
from time import sleep
sys.path.append('/home/pi/kindbot/utils/')
from utils import day_time


def sock_comm(comm, dev_idx):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 9000))
        data = dev_idx + " " + comm
        sock.sendall(data.encode())
        result = sock.recv(1024).decode()
        print(result)
        sock.close()
    except:
        sock.close()

def day_runner(dev_idx):
    if day_time():
        sock_comm('on', dev_idx)
    while day_time():
        sleep(600)
    else:
        sock_comm('off', dev_idx)
        sys.exit(0)

if __name__ == "__main__":
    dev_idx = sys.argv[1]
    day_runner(dev_idx)

