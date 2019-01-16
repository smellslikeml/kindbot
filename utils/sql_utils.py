#!/usr/bin/env python
import sqlite3
import numpy as np
from datetime import datetime
import configparser
from operator import itemgetter
from itertools import groupby

config = configparser.ConfigParser()
config.read('/home/pi/kindbot/config.ini')


def create_tbl(table_name, schema_tup):
    conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
    c = conn.cursor()
    c.execute('''drop table if exists {};'''.format(table_name))
    c.execute('''create table {} 
    {}'''.format(table_name, schema_tup))
    conn.commit()
    c.close()

def by_the_hour(dt):
    return dt[:13]

def reduce_by_hour(group):
    x, y = zip(*list(group))
    return x[0], sum(y)


def energy_timeline(start_date, end_date=None):
    conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
    c = conn.cursor()
    if end_date is None:
        c.execute('''select date, energy_consumption from devices where date >= "{}";'''.format(start_date))
    else:
        c.execute('''select date, energy_consumption from devices where date between "{}" and "{}";'''.format(start_date, end_date))
    res = c.fetchall()
    c.close()
    x, y = zip(*res)
    x = map(by_the_hour, x)
    y = np.cumsum(y)
    res = zip(x, y)
    return [reduce_by_hour(group) for _, group in groupby(res, key=itemgetter(0))]

def energy_cons(start_date, end_date=None):
    conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
    c = conn.cursor()
    if end_date is None:
        c.execute('''select SUM(energy_consumption) from devices where date >= "{}";'''.format(start_date))
    else:
        c.execute('''select SUM(energy_consumption) from devices where date between "{}" and "{}";'''.format(start_date, end_date))
    res = c.fetchall()[0][0]
    c.close()
    return res

def env_stats(start_date, end_date=None):
    conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
    c = conn.cursor()
    if end_date is None:
        c.execute('''select * from environ where date >= "{}";'''.format(start_date))
    else:
        c.execute('''select * from environ where date between "{}" and "{}";'''.format(start_date, end_date))
    res = c.fetchall()
    c.close()
    return res

def env_timeline(view='day'):
    conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
    c = conn.cursor()
    if view == 'day':
        c.execute('''select * from environ where rowid > 0 and rowid % 30 = 0 order by rowid desc limit 48;''')
    elif view == 'week':
        c.execute('''select * from environ where rowid > 0 and rowid % 700 = 0 order by rowid desc limit 14;''')
    elif view == 'month':
        c.execute('''select * from environ where rowid > 0 and rowid % 5000 = 0 order by rowid desc limit 10;''')
    res = c.fetchall()
    c.close()
    return res


def alert_check(stat, dev=1):
    conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
    c = conn.cursor()
    c.execute('select date, {} from objects order by rowid desc limit 50;'.format(stat))
    data = c.fetchall()
    c.close()

    dt, stat_series = zip(*data)
    stats = list(zip(dt, stat))
    st, mn = np.std(stat_series[:-1]), np.median(stat_series[:-1])
    high = mn + dev * st
    low = mn - dev * st
    val = stat_series[-1]
    dd = dt[-1]
    alert = None
    if high < val:
        alert = 'High'
    elif val < low:
        alert = 'Low'
    if alert:
        conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
        c = conn.cursor()
        c.execute("""insert into alerts values (?, ?, ?)""", (dd, val, 'Alert: {} {}'.format(alert, stat)))
        conn.commit()
        c.close()

if __name__ == '__main__':
    table_dict = {'environ':'(date date, temp real, hum real, vpd real)', 
                  'devices':'(date text, plug int, duration real, energy_consumption real)',
                  'kindbot':'(date text, temp real, humid real, pid real, vpd real, ac text)',
                  'objects':'(img text, date text, flower int, yellow int, droop int, lai real)',
                  'alerts':'(date text, level real, alert text)'}
    BUILD_TBLS = False
    if BUILD_TBLS:
        for table_name, schema_tup in table_dict.items():
            create_tbl(table_name, schema_tup)

    print(env_timeline(view='day'))
