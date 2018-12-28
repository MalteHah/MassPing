"""
This script adds a new device to MassPing

* add to devicelist
"""

# Config
devicelist = 'devicelist.txt'

file = open(devicelist, 'a')

hostname = input("Hostname: ")
ip = input("IP address: ")
location = input("Location: ")
function = input("Function: ")

file.write(ip + " " + hostname + "" + location + " " + function + "\n")

file.close()
