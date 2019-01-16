#!/usr/bin/python3
import sqlite3
import numpy as np
import configparser
from glob import glob
from time import sleep, strftime
from datetime import datetime
from darkflow.net.build import TFNet

config = configparser.ConfigParser()
config.read('/home/pi/kindbot/config.ini')

def on_off_bin(ac):
    if ac == 'on':
        return 1
    else:
        return 0 

def fmt_tup(tup):
    setpoint = float(config['DAYTIME']['SETPOINT'])
    return ((tup[1] - setpoint) / 20, tup[2] / 100, tup[3] / 2, on_off_bin(tup[4]))


def data_stream():
    conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
    c = conn.cursor()
    res = c.execute("""select date, temp, humid, vpd, ac from kindbot order by rowid desc limit 5;""")
    data = [val for val in res]
    c.close()
    data = data[::-1]
    tm = (int(data[0][0][11:13]) - 12.) / 12
    data = list(map(fmt_tup, data))
    data = [x for v in data for x in v]
    return data + [tm]

def vpd_lin_trans(vpd, min_v=1.0, max_v=2.0, max_rate=1.0, min_rate=0.15):
    vpd = (np.clip(vpd, min_v, max_v) - min_v) / (max_v - min_v)
    return 1  / (vpd * (max_rate - min_rate) + min_rate)

def on_off(dev_idx, duration):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9000))
    data = dev_idx + " on"
    sock.sendall(data.encode())
    result = sock.recv(1024).decode()
    print(result)
    sock.close()

    sleep(duration)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9000))
    data = dev_idx + " off"
    sock.sendall(data.encode())
    result = sock.recv(1024).decode()
    print(result)
    sock.close()

def day_time():
    start_hour = int(config['DAYTIME']['ON_START'])
    end_hour = int(config['DAYTIME']['ON_DURATION'])
    end_hour = (start_hour + end_hour) % 24
    cur_hour = datetime.now().time().hour
    return (cur_hour < end_hour) or (cur_hour >= start_hour)

def gif_gen():
    import subprocess
    from os import chdir
    chdir('/home/pi/timelapse/')
    img_lst = sorted(glob('./*.jpg'))
    img_lsts = img_lst[-300:][::20]

    with open('gif_list.txt', 'w') as gif_file:
        for itm in img_lsts:
            gif_file.write('%s\n' %itm)
        
    subprocess.call('convert -delay 10 @gif_list.txt recent.gif', shell=True)

def tl_photo(img_pth='/home/pi/timelapse/{}.jpg'.format(strftime("%Y%m%d-%H%M%S"))):
    import picamera
    camera = picamera.PiCamera(resolution=(1280, 720))
    sleep(2)
    camera.shutter_speed = camera.exposure_speed
    camera.iso = 100
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    g = camera.awb_gains
    camera.awb_gains = g
    camera.capture(img_pth)
    return

def label_filter_box(itm, lbl, conf=0.1):
    if (itm['label'] == lbl) and (itm['confidence'] > conf):
        x1, y1 = itm['bottomright']['x'], itm['bottomright']['y']
        x2, y2 = itm['topleft']['x'], itm['topleft']['y']
        return x1, y1, x2, y2

def annotate(imgcv, res, lbl):
    x1, y1, x2, y2 = res
    x_diff = max(int((x1 - x2) / 5), 5)
    y_diff = max(int((y1 - y2) / 5), 5)

    color_dict = {'yellow_leaf': (0, 255, 255), 
                  'flower': (0, 0, 255), 
                  'droop': (255, 255, 0)}
    img_c = imgcv.copy()
    cv2.line(img_c, (x1 , y1), (x1, y1 - y_diff), color_dict[lbl], 3)
    cv2.line(img_c, (x1 - x_diff, y1), (x1, y1), color_dict[lbl], 3)
    cv2.line(img_c, (x2 + x_diff, y2), (x2, y2), color_dict[lbl], 3)
    cv2.line(img_c, (x2, y2), (x2, y2 + y_diff), color_dict[lbl], 3)
    cv2.putText(img_c, lbl.title(), (x2, y2), cv2.FONT_HERSHEY_TRIPLEX, 0.7, color_dict[lbl], 1, cv2.LINE_AA)
    cv2.addWeighted(img_c, 0.7, imgcv, 0.3, 0, imgcv)
    return
