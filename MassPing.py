#!/usr/local/bin/python3.6

"""
MassPing.py

script loading a file with a list of devices to ping, then pings the devices, then puts
the results into a webpage

v1      2017-1217       jadavis Initial version
v2  2018-0118   jadavis Updated to tag influxdb data with hostname as supplied in devicelist;
                                                also removed HTML web page creation in lieu of using Grafana

TODO: 

* devicelist wird vor jedem Ping neu eingelesen. Bug oder feature? 
  --> Feature! Denn sonst müsste man bei jeder Änderung den Dienst neu starten.
* stderr einfangen über den logger
* logrotate mit logger --> erledigt

"""

import shlex
from subprocess import check_output, Popen, PIPE
import re
import requests
# import schedule
import time
import datetime
import logging.handlers

## User defined vars
devicelist = "devicelist.txt"
influxserver = "localhost"  # hostname or IP of InfluxDB server
databasename = "MassPing"  # name of existing InfluxDB database
##

logger = logging.getLogger('MassPing')


def get_fping_output(cmd):
    args = shlex.split(cmd)
    proc = Popen(args, stdout=PIPE, stderr=PIPE, encoding='utf8')
    out, err = proc.communicate()
    exitcode = proc.returncode
    return exitcode, out, err


def load_devicefile():
    iplist = dict()
    with open(devicelist) as file:
        for line in file:
            line = line.strip()  # preprocess line
            ipaddress, hostname, location, function = line.split()
            iplist[ipaddress] = [hostname, location, function]
    logger.info('Loading devicelist')
    return iplist


def getpingresults():
    iplist = dict(load_devicefile())
    cmd = "/usr/local/sbin/fping -C 3 -A -q {}".format(" ".join(map(str, iplist.keys())))
    exitcode, out, results = get_fping_output(cmd)

    for aline in results.split("\n"):
        logger.debug('Working on line: {0}'.format(aline))
        if aline:
            m = re.match(r"(\S+)\s+:\s(\S+)", aline)
            ipaddress = m.group(1)
            rtt = m.group(2)
            if rtt == '-':
                iplist[ipaddress] += (float(9999),)
            else:
                iplist[ipaddress] += (float(rtt),)

    logger.info('get ping results')
    return iplist


def createtabledata():
    iplist = getpingresults()
    influxdata = []
    for key, values in iplist.items():
        influxentry = "ping,host=" + key + ",hostname=" + values[0] + ",location=" + values[1] + ",function=" + values[
            2] + " rtt=" + str(values[3])
        influxdata.append(influxentry)

    influxdata = '\n'.join(influxdata)
    logger.info('ab in die DB damit')
    return influxdata


def write2influx():
    influxdata = createtabledata()
    url = "http://localhost:8086/write"
    params = {"db": databasename}
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
    }
    response = requests.request("POST", url, data=influxdata, headers=headers, params=params)
    print(response.text)


def dowork():
    logger.info("Started...")
    write2influx()
    logger.info("Done...")


log_filename = '/var/log/MassPing.log'
file_handler = logging.handlers.RotatingFileHandler(log_filename,
                                                    mode='a',
                                                    maxBytes=2000000,
                                                    backupCount=5)
fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(fmt)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# TODO: macht noch Probleme mit logger
# schedule.every(10).seconds.do(dowork)

while True:
    # schedule.run_pending()
    dowork()
    time.sleep(10)
