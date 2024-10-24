# # 
# Firmware adapted from https://github.com/RequestForCoffee/scd30
import datetime
from datetime import timedelta
import logging
import smbus2
import struct
import time
import bme280
import math
import adafruit_gps

class PA1010D:

    def __init__(self, i2c_dev,debugIn):
        self.i2c      = i2c_dev
        self.debug    = debugIn

    def initiate(self):
        print("============== PA1010D ==============")
        try:
            print("Initiating PA1010D")
            self.pa1010d = adafruit_gps.GPS_GtopI2C(self.i2c, debug=False) # Use I2C interface
            print("GPS found")
            # Turn on everything (not all of it is parsed!)
            print("Sending GPS Command")
            self.pa1010d.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
            time.sleep(.1)
            print("Changing Update Frequency")
            self.pa1010d.send_command(b"PMTK220,100")
            return True
        
        except KeyboardInterrupt:
            return False

        except Exception as e:
            time.sleep(5)
            print("An exception occurred:", type(e).__name__, "–", e) 
            time.sleep(5)
            print("PA1010D Not Found")
            return False

    def read(self):
        dateTime = datetime.datetime.now()
        if not self.pa1010d.update() or not self.pa1010d.has_fix:
            # print("No Coordinates found")
            # print(self.pa1010d.nmea_sentence) 
            return [False,dateTime,self.pa1010d.nmea_sentence]
        else:
            return [True,dateTime,self.pa1010d.nmea_sentence] 
        