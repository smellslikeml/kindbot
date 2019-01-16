#!/usr/bin/env python3
import sys
import subprocess


if __name__ == "__main__":
    import configparser
    config = configparser.ConfigParser()
    config.read('/home/pi/kindbot/config.ini')

    controller = sys.argv[1]

    for plug in config:
        if config[plug].get('MODE', None) == controller:
            if controller in ['daytime', 'rl', 'pid']:
                arg_tup = (config[plug]['DEV_IDX'], )
                if controller == 'daytime':
                    subprocess.call('nohup /home/pi/kindbot/img_srv.py > /home/pi/img_srv.log 2>&1 &', shell=True)
            elif controller == 'regular':
                arg_tup = (config[plug]['DEV_IDX'], config[plug]['ON_DURATION'], config[plug]['ON_EVERY'])
            elif controller == 'vpd':
                arg_tup = (config[plug]['DEV_IDX'], config[plug]['ON_DURATION'])
            subprocess.call('nohup /home/pi/kindbot/control/{}_procs.py {} &'.format(controller, *arg_tup), shell=True)


