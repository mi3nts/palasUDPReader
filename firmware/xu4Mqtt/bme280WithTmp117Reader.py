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
#from i2cMints.i2c_scd30 import SCD30
from i2cMints.i2c_bme280v3 import BME280V3
from i2cMints.i2c_tmp117 import TMP117
from mintsXU4 import mintsSensorReader as mSR

debug        = False 
bus          = smbus2.SMBus(5)

# BME280V3
bme280v3       = BME280V3(bus,debug)

# TMP117
tmp117       = TMP117(bus,debug) 

checkTrials  = 0
loopInterval = 5 

def main(loopInterval):
    bme280v3_valid   = bme280v3.initiate(30)
    tmp117_valid     = tmp117.initiate(30)
    
    startTime    = time.time()
    while True:
        try:
            print("======= BME280V3 ========")
            if bme280v3_valid:
                mSR.BME280V3WriteI2c(bme280v3.read())
            time.sleep(1)     
            
            print("======= TMP117 ========")
            if tmp117_valid:
                mSR.TMP117WriteI2c(tmp117.read())

            print("=======================")
            time.sleep(1)       
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