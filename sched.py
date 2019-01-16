#!/usr/bin/python
import configparser
from crontab import CronTab

# TODO: find jobs to schedule under MODE='sched'
# in config.ini, rebuild crontab periodically
config = configparser.ConfigParser()
config.read('/home/pi/kindbot/config.ini')

cron = CronTab(user='pi')
iter = cron.find_command('daytime')
start_hour = config['DAYTIME']['ON_START']
for line in iter:
    ll = str(line)
    if ll.startswith('0'):
        cron.remove(line)

for mode in ['rl', 'daytime']:
    job = cron.new('/home/pi/kindbot/runner.py {} > /home/pi/{}.log 2>&1'.format(mode, mode))
    job.hour.on(start_hour)
    job.minute.on(0)
    cron.write()
