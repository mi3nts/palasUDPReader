from datetime import timezone
import time
import os
import datetime
import netifaces as ni
from collections import OrderedDict
import netifaces as ni
from requests import get
import yaml
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions  as mD

dataFolder = mD.dataFolder

# # This can be a list 
# wearablesFile   = mD.wearablesFile
# wearablesData   = yaml.load(open(wearablesFile))


import os



def main():
    sensorName = "IP"
    dateTimeNow = datetime.datetime.now()
    print("Gaining Public and Private IPs")

    # Fetch public IP
    publicIp = get('https://api.ipify.org').text

    # Initialize ip as None in case no valid IP is found
    localIp = None

    # Get all available network interfaces
    interfaces = ni.interfaces()
    for interface in interfaces:
        try:
            # Check if this interface has an IPv4 address
            ip = ni.ifaddresses(interface).get(ni.AF_INET)
            if ip:
                localIp = ip[0]['addr']
                break  # Stop once we find the first valid IP
        except ValueError:
            continue  # If an interface has no IP or is unavailable, skip it

    # Check if a local IP was found, otherwise set a default or error message
    if localIp is None:
        localIp = "No valid local IP found"

    # Create the sensor dictionary to pass to the sensor finisher
    sensorDictionary = OrderedDict([
        ("dateTime", str(dateTimeNow)),
        ("publicIp", str(publicIp)),
        ("localIp", str(localIp))
    ])

    # Call the sensor finisher
    mSR.sensorFinisherIP(dateTimeNow, sensorName, sensorDictionary)

if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    main()
