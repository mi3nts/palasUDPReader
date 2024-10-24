#!/usr/bin/python
# ***************************************************************************
#   I2CPythonMints
#   ---------------------------------
#   Written by: Lakitha Omal Harindha Wijeratne
#   - for -
#   MINTS :  Multi-scale Integrated Sensing and Simulation
#     & 
#   TRECIS: Texas Research and Education Cyberinfrastructure Services
#
#   ---------------------------------
#   Date: July 7th, 2022
#   ---------------------------------
#   This module is written for generic implimentation of MINTS projects
#   --------------------------------------------------------------------------
#   https://github.com/mi3nts
#   https://trecis.cyberinfrastructure.org/
#   http://utdmints.info/
#  ***************************************************************************



import sys
import time
import os
import smbus2

from i2cMints.i2c_ips7100 import IPS7100
from mintsXU4 import mintsSensorReader as mSR

debug        = False 
bus          = smbus2.SMBus(3)

# IPS7100
ips7100      = IPS7100(bus,debug)

checkTrials  = 0
loopInterval = 1 

def main(loopInterval):
    ips7100_valid   = ips7100.initiate(30)
    
    startTime    = time.time()
    while True:
        try:
            print("======= IPS7100 ========")
            if ips7100_valid:
                mSR.IPS7100WriteI2c(ips7100.read())
            time.sleep(.5)    
            startTime = mSR.delayMints(time.time() - startTime,loopInterval)
            
        except Exception as e:
            print(e)
            time.sleep(10)


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print("Monitoring Climate data for MASK")
    main(loopInterval)