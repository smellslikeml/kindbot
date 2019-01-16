# Kindbot: Home Gardening meets Home Automation

The Kindbot garden controller maintains ideal environmental conditions for indoor grow spaces using inexpensive hardware leveraging the state-of-the-art in embedded AI.

![kindbot](https://github.com/mayorquinmachines/kindbot/blob/master/kindbot_an_intro.gif?raw=true)

### Features
 * RL temperature control on device
 * Log environmental data and visualize grow stats
 * Control and schedule appliances via smart plugs
 * Monitor plant health via [Buddy diagnostics](https://buddy.kindbot.io)

Learn more about Kindbot by visiting:
 * [Kindbot.io](http://kindbot.io/)
 * [Hackster](https://www.hackster.io/kindbot/kindbot-smart-home-gardening-4c218a)
 * [Instagram](https://www.instagram.com/kindbot/)

# Dependencies


## Tools
 * Soldering Iron
 * 3D printer


## Hardware
 * [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero/)
 * [BME280 temperature/humidity sensor](https://www.adafruit.com/product/2652)
 * [TP-Link Kasa HS300 SmartStrip](https://www.kasasmart.com/us/products/smart-plugs/kasa-smart-wi-fi-power-strip-hs300)
 * 8 GB MicroSD card
 * picamera
 * Standard USB to micro-USB power supply
 * 1/4 inch hex nut
 * 4 - 3mm phillips head machine screws
 * Mini HDMI adapter and Monitor

## Software
 * [Tensorflow for raspberry pi](https://github.com/samjabrahams/tensorflow-on-raspberry-pi)
 * [Adafruit BME280 Library](https://github.com/adafruit/Adafruit_BME280_Library)
 * [pyHS100](https://github.com/GadgetReactor/pyHS100)
 * [Flask](http://flask.pocoo.org/)
 * [pysqlite](https://pypi.org/project/pysqlite/)
 * [opencv](https://pypi.org/project/opencv-python/)

# Getting Started

Use the associated CAD files to 3D print the Kindbot case. 
Note that to insert the camera mount nut, you will need to pause the print of the Kindbot case top/face roughly 25% through to drop in the nut.
![wiring diagram](http://kindbot.io/images/kindbot_diagram.png)

Follow the wiring diagram to solder the environmental sensor breakout to the GPIO pins of the raspberry pi and connect the camera using the ribbon cable.
Insert this assembly into the Kindbot case and seal with the machine screws.
![assembly](https://github.com/mayorquinmachines/kindbot/blob/master/assemble_kindbot.gif?raw=true)

Connect the mini-HDMI adapter and a monitor, open a terminal, and go through the installation.

## Installation

Change the config.ini file to reflect the wifi network name and password.
Configure the additional parameters to schedule events, change temperature setpoints, etc.
You may decide to set a [static IP](https://www.modmypi.com/blog/tutorial-how-to-give-your-raspberry-pi-a-static-ip-address) to simplify access to the web server.

Run the install bash script.
```
bash install.sh
```

## Setup

Connect appliances like fans, AC units, irrigation pumps, and lights to the smart strip according to the configuration of plugs you set in the config.ini file.

Mount the Kindbot device in your grow space using standard camera mounting hardware. 
Position the camera to tightly frame the subject in your garden you wish to monitor.

From another machine on the local network, access the Flask application using a browser to navigate to KINDBOT_IP:5000 to view the camera stream, review environmental statistics, and control your Kindbot device.


# Contributing

Have an idea for improvements? Reach out by raising an issue.

# License

This project is released under the GNU AGPLv3, a copyleft license granting broad permissions while disallowing the distribution of a closed source version of this work.
See more details in the LICENSE.md file.
