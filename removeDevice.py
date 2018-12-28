"""
# Dieses Skript Löscht ein Device aus dem MassPing

* Device aus der Device-List Löschen
* Alte Daten aus der Influx-Datenbank Löschen

## Aufruf: removeDevice.py <devicename>
"""

import sys
import requests


# Argumente übernehmen
if len(sys.argv) <= 1:
    print("usage: removeDevice.py <devicename>")
    quit()

host = sys.argv[1]

# Config
devicelist = 'devicelist.txt'
databasename = 'MassPing'
influxUrl = 'http://localhost:8086/'


def deleteDeviceFromDevicelist(host):
    with open(devicelist, 'r+') as file:
        r = False
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            line = line.strip()  # preprocess line
            ipaddress, hostname, location, function = line.split()
            if host not in line:
                file.write(line + "\n")
            else:
                print(host + "removed from devicelist!")
                r = True
        file.truncate()
    return r


def deleteDeviceFromInfluxDB(host):
    print("delete measurements from influxDB")
    url = influxUrl + 'query'
    data = {
        'db': databasename,
        'q': 'drop Series from ping where "hostname" = \'' + host + '\''
    }
    r = requests.post(url, data)
    print(r.text)
    print(url)
    print(data)


if deleteDeviceFromDevicelist(host) is True:
    deleteDeviceFromInfluxDB(host)
else:
    print("Device " + host + "not found on devicelist!")
