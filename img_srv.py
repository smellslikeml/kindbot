#!/usr/bin/env python3
import cv2
import sys
import imutils
import sqlite3
import configparser
sys.path.append('/home/pi/kindbot/')
sys.path.append('/home/pi/kindbot/utils/')
sys.path.append('/home/pi/darkflow/')
sys.path.append('/home/pi/darknet/')
from datetime import datetime
from time import sleep, strftime
from numpy import mean, max
from collections import Counter

config = configparser.ConfigParser()
config.read('/home/pi/kindbot/config.ini')


class img_alz:
    def __init__(self, img_pth=None):
        self.tfnet = None
        self.avg = None

        if img_pth is None:
            self.img_pth = '/tmp/stream/pic.jpg'
        else:
            self.img_pth = img_pth

    def load_img(self):
        self.img = cv2.imread(self.img_pth, 1)

    def save_img(self, img_pth=None):
        if img_pth is None:
            dt = strftime("%Y%m%d-%H%M%S")
            img_pth = '/home/pi/timelapse/{}.jpg'.format(dt)
        cv2.imwrite(img_pth, self.img)
        return img_pth
        
    def leaf_area_index(self):
        mask = cv2.inRange(self.img, (30, 0, 0), (80, 255,255))
        self.lai = mean(mask>0)
        return self.lai

    def luminosity(self):
        lights = max(self.img)
        self.lights = True if lights > 10 else False
        return self.lights

    def load_model(self):
        from darkflow.net.build import TFNet
        chdir('/home/pi/darkflow/')
        options = {"model": "/home/pi/darkflow/cfg/tiny-yolo-budnet_new.cfg", 
                   "load": "/home/pi/darkflow/tiny-yolo-budnet_new_final.weights", "threshold": 0.01}
        self.tfnet = TFNet(options)
        return 
        
    def run_inference(self):
        if not self.tfnet:
            self.load_model()
        self.result = self.tfnet.return_predict(self.img)
        meta_dict = dict(Counter([itm['label'] for itm in self.result]))
        return meta_dict
        
    def motion_detector(self):
        occupied = False
        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(self.img, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
     
        if self.avg is None:
            print("[INFO] starting background model...")
            self.avg = gray.copy().astype("float")
     
        # accumulate the weighted average between the current frame and
        # previous frames, then compute the difference between the current
        # frame and running average
        cv2.accumulateWeighted(gray, self.avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))
        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frameDelta, 5, 255,
            cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
     
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 5000:
                pass
            occupied = True
     
        # check to see if the room is occupied
        if occupied:
            # check to see if enough time has passed between uploads
            print('occupied')
            cv2.imwrite('/home/pi/videos/' + strftime("%Y%m%d-%H%M%S") + '.jpg', frame)
        return occupied


if __name__ == '__main__':
    from os import chdir
    from utils import day_time

    ia = img_alz()
    while day_time():
        if datetime.now().time().minute % 10 == 0:
            ia.load_img()
            lai = 0
            dt = str(datetime.now()).split('.')[0]
            if ia.luminosity():
                ia.motion_detector()
                meta_dict = ia.run_inference()
                lai = round(ia.leaf_area_index(), 2)
                new_img = ia.save_img()
                conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
                c = conn.cursor()
                c.execute("""insert into objects values (?, ?, ?, ?, ?, ?)""", (new_img, dt, round(meta_dict.get('flower', 0), 2), round(meta_dict.get('yellow_leaf', 0), 2), round(meta_dict.get('droop', 0), 2), lai))
                conn.commit()
                c.close()
            else:
                alert = 'lights out'
                print(alert)
                c = conn.cursor()
                c.execute("""insert into alerts values (?, ?, ?)""", (dt, 0, alert))
                conn.commit()
                c.close()
        sleep(60)
    else:
        sys.exit(0)

