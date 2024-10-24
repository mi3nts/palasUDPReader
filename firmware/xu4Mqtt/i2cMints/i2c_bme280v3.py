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

# to_s16 = lambda x: (x + 2**15) % 2**16 - 2**15
# to_u16 = lambda x: x % 2**16

BME280_I2C_ADDR = 0x77

class BME280V3:

    def __init__(self, i2c_dev,debugIn):
        
        self.i2c_addr = BME280_I2C_ADDR
        self.i2c      = i2c_dev
        self.debug    = debugIn

    def initiate(self,retriesIn):
        print("============== BME280V3 ==============")
        ready = None
        while ready is None and retriesIn:
            try:
                self.calibration_params = bme280.load_calibration_params(self.i2c, self.i2c_addr)
                ready = True
                
            except OSError:
                pass
            time.sleep(1)
            retriesIn -= 1

        if not retriesIn:
            time.sleep(1)
            return False
        
        else:
            print("BME 280 Found - Calibraion Params Set")
            time.sleep(1)
            return True       
        
    def calculate_dew_point(self,temp, humid):
        dew_point = 243.04 * (math.log(humid / 100.0) + ((17.625 * temp) / (243.04 + temp))) / (17.625 - math.log(humid / 100.0) - ((17.625 * temp) / (243.04 + temp)))
        return dew_point
    
    def calculate_altitude(self,pressure):
        A = (100*pressure) / 101325;
        B = 1 / 5.25588
        C = pow(A, B)
        C = 1.0 - C
        return C/0.0000225577;
             

    def read(self):
        dateTime = datetime.datetime.now() 
        measurement = bme280.sample(self.i2c, self.i2c_addr, self.calibration_params)
        if measurement is not None:
            return [dateTime,\
                    measurement.temperature,\
                        100*measurement.pressure,\
                            measurement.humidity,\
                                self.calculate_dew_point(measurement.temperature, measurement.humidity),\
                                    self.calculate_altitude(measurement.pressure)];
        else:
            time.sleep(1)
            print("BME280 Measurments not read")    
            return [];