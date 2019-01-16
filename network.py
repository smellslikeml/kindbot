#!/usr/bin/python2
import configparser

config = configparser.ConfigParser()
config.read('/home/pi/kindbot/config.ini')

ssid = config['PATHS']['NETWORK_SSID']
pwd = config['PATHS']['NETWORK_PWD']
if not len(ssid):
    ssid = raw_input('Enter the name of the network: ')
    pwd = raw_input('Enter the network password: ')

net_str = '''network={
    ssid="%s"
    psk="%s"
}
''' %(ssid, pwd)

if __name__ == '__main__':
    # sudo python network.py
    import sys
    sys.stdout = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w')
    print(net_str)
