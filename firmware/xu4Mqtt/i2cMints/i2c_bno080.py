# # 
# Firmware adapted from https://github.com/RequestForCoffee/scd30
import datetime
from datetime import timedelta
import logging
import smbus2
import struct
import time
from math import atan2, sqrt, pi

from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_extended_bus import ExtendedI2C as I2C

from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
    BNO_REPORT_LINEAR_ACCELERATION,
    BNO_REPORT_STEP_COUNTER,
    BNO_REPORT_STABILITY_CLASSIFIER,
    BNO_REPORT_ACTIVITY_CLASSIFIER,
    BNO_REPORT_SHAKE_DETECTOR,
)

# from adafruit_bno08x import (
#     BNO_REPORT_ACCELEROMETER,
#     BNO_REPORT_GYROSCOPE,
#     BNO_REPORT_ROTATION_VECTOR,
# )


# # to_s16 = lambda x: (x + 2**15) % 2**16 - 2**15
# # to_u16 = lambda x: x % 2**16

# BME280_I2C_ADDR = 0x77
mapping  =  {
                'Unknown': 0,
                'In-Vehicle': 1,
                'On-Bicycle': 2,
                'On-Foot': 3,
                'Still': 4,
                'Tilting': 5,
                'Walking': 6,
                'Running': 7,
                'OnStairs': 8
            }


class BNO080:

    def __init__(self, i2c_dev,debugIn):
        
        # self.i2c_addr = BME280_I2C_ADDR
        self.i2c      = i2c_dev
        self.debug    = debugIn

    def initiateV2(self):
        try:
            print("Initiating BNO")
            self.bno = BNO08X_I2C(self.i2c)
            time.sleep(1)
            print("Initiating ACC")
            self.bno.enable_feature(BNO_REPORT_ACCELEROMETER)
            time.sleep(1)
            print("Initiating GYR")
            self.bno.enable_feature(BNO_REPORT_GYROSCOPE)
            time.sleep(1)            
            print("Initiating ROT")
            self.bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
            time.sleep(1)     
            print("BNO080 Found")
            time.sleep(1)
            return True     

        except KeyboardInterrupt:
            self.reset()
            return False


        except Exception as e:
            time.sleep(5)
            print("An exception occurred:", type(e).__name__, "–", e) 
            time.sleep(5)
            print("BNO080 Not Found")
            return False
    def initiate(self):
        try:
            print("Initiating BNO")
            self.bno = BNO08X_I2C(self.i2c)
            time.sleep(1)   
            print("Initiating ACT")            
            self.bno.enable_feature(BNO_REPORT_ACTIVITY_CLASSIFIER)
            time.sleep(1)
            print("Initiating ACC")
            self.bno.enable_feature(BNO_REPORT_ACCELEROMETER)
            time.sleep(1)
            print("Initiating GYR")
            self.bno.enable_feature(BNO_REPORT_GYROSCOPE)
            time.sleep(1)            
            print("Initiating MAG")
            self.bno.enable_feature(BNO_REPORT_MAGNETOMETER)
            time.sleep(1)
            print("Initiating ROT")
            self.bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
            time.sleep(1)   
            print("Initiating LINACC")         
            self.bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
            time.sleep(1)     
            print("Initiating STEP")          
            self.bno.enable_feature(BNO_REPORT_STEP_COUNTER)
            time.sleep(1)
            print("Initiating STAB")   
            self.bno.enable_feature(BNO_REPORT_STABILITY_CLASSIFIER)
            time.sleep(1)     
            print("Initiating SHK")          
            self.bno.enable_feature(BNO_REPORT_SHAKE_DETECTOR)
            time.sleep(1)    
            # ready = True
            # print("Initiating BNO")
            # self.bno = BNO08X_I2C(self.i2c)
            # time.sleep(1)
            # print("Initiating ACC")
            # self.bno.enable_feature(BNO_REPORT_ACCELEROMETER)
            # time.sleep(1)
            # print("Initiating GYR")
            # self.bno.enable_feature(BNO_REPORT_GYROSCOPE)
            # time.sleep(1)            
            # print("Initiating ROT")
            # self.bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
            # time.sleep(1)     
          
            print("BNO080 Found")
            time.sleep(1)
            return True     

        except KeyboardInterrupt:
            self.reset()
            return False


        except Exception as e:
            time.sleep(5)
            print("An exception occurred:", type(e).__name__, "–", e) 
            time.sleep(5)
            print("BNO080 Not Found")
            return False

  
    def softReset(self):
        time.sleep(1)
        self.bno.soft_reset()
        time.sleep(1)


    def hardReset(self):
        time.sleep(1)
        self.bno.hard_reset()
        time.sleep(1)


    def reset(self):
        time.sleep(1)
        print("Resetting the sensor")
        # self.bno.hard_reset()
        time.sleep(1)
        # self.bno.soft_reset()
        time.sleep(1)


    def find_heading(self,dqw, dqx, dqy, dqz):
        norm = sqrt(dqw * dqw + dqx * dqx + dqy * dqy + dqz * dqz)
        dqw = dqw / norm
        dqx = dqx / norm
        dqy = dqy / norm
        dqz = dqz / norm

        ysqr = dqy * dqy

        t3 = +2.0 * (dqw * dqz + dqx * dqy)
        t4 = +1.0 - 2.0 * (ysqr + dqz * dqz)
        yaw_raw = atan2(t3, t4)
        yaw = yaw_raw * 180.0 / pi
        if yaw > 0:
            yaw = 360 - yaw
        else:
            yaw = abs(yaw)
        return yaw  # heading in 360 clockwise
    

    def activity_classification_summary(self,activity_classification):
        most_likely       = activity_classification["most_likely"]
        most_likely_index = mapping.get(activity_classification['most_likely'], -1) 
        most_likely_conf  = activity_classification[most_likely]
        outPut            = [ most_likely_index,\
                            most_likely_conf,\
                            activity_classification["Unknown"], \
                            activity_classification["In-Vehicle"], \
                            activity_classification["On-Bicycle"], \
                            activity_classification["On-Foot"], \
                            activity_classification["Still"], \
                            activity_classification["Tilting"], \
                            activity_classification["Walking"], \
                            activity_classification["Running"], \
                            activity_classification["OnStairs"] \
                        ]
        return outPut;

    def shake_summary(self,shake_output):
        if shake_output == False:
            return 0
        
        return 1; 


    def read(self):
        try:
            dateTime                                            = datetime.datetime.now() 
            time.sleep(.1)
            accel_x, accel_y, accel_z                           = self.bno.acceleration  # pylint:disable=no-member
            time.sleep(.1)            
            linear_accel_x,linear_accel_y, linear_accel_z       = self.bno.linear_acceleration
            time.sleep(.1)            
            gyro_x, gyro_y, gyro_z                              = self.bno.gyro  # pylint:disable=no-member
            time.sleep(.1)            
            mag_x, mag_y, mag_z                                 = self.bno.magnetic  # pylint:disable=no-member
            time.sleep(.1)            
            quat_i, quat_j, quat_k, quat_real                   = self.bno.quaternion  # pylint:disable=no-member
            time.sleep(.1)            
            heading                                             = self.find_heading(quat_real, quat_i, quat_j, quat_k)
            time.sleep(.1)            
            steps                                               = self.bno.steps
            time.sleep(.1)
            shake                                               = self.shake_summary(self.bno.shake)
            [   most_likely_index,\
                most_likely_conf,\
                unknown, \
                in_vehicle, \
                on_bicycle, \
                on_foot, \
                still, \
                tilting, \
                walking, \
                running, \
                on_stairs \
                ]                                                = self.activity_classification_summary(self.bno.activity_classification)


            return [dateTime,\
                    accel_x, accel_y, accel_z,\
                    linear_accel_x,linear_accel_y, linear_accel_z,\
                    gyro_x, gyro_y, gyro_z,\
                    mag_x, mag_y, mag_z,\
                    quat_i, quat_j, quat_k, quat_real,\
                    heading,\
                    steps ,\
                    shake,\
                    most_likely_index,\
                    most_likely_conf,\
                    unknown, \
                    in_vehicle, \
                    on_bicycle, \
                    on_foot, \
                    still, \
                    tilting, \
                    walking, \
                    running, \
                    on_stairs\
                  ];
    
        except Exception as e:
            time.sleep(5)
            self.reset()
            print("An exception occurred:", type(e).__name__, "–", e) 
            time.sleep(5)
            return [];



    def readV2(self):
        # try:
        dateTime                                            = datetime.datetime.now() 
        time.sleep(.1)
        accel_x, accel_y, accel_z                           = self.bno.acceleration  # pylint:disable=no-member
        # time.sleep(.1)            
        # linear_accel_x,linear_accel_y, linear_accel_z       = self.bno.linear_acceleration
        time.sleep(.1)            
        gyro_x, gyro_y, gyro_z                              = self.bno.gyro  # pylint:disable=no-member
        time.sleep(.1)            
        # mag_x, mag_y, mag_z                                 = self.bno.magnetic  # pylint:disable=no-member
        # time.sleep(.1)            
        quat_i, quat_j, quat_k, quat_real                   = self.bno.quaternion  # pylint:disable=no-member
        time.sleep(.1)            
        heading                                             = self.find_heading(quat_real, quat_i, quat_j, quat_k)
        return [dateTime,\
                accel_x, accel_y, accel_z,\
                gyro_x, gyro_y, gyro_z,\
                quat_i, quat_j, quat_k, quat_real,\
                heading,\
                ];
    
        # except Exception as e:
        #     time.sleep(5)
        #     print("An exception occurred:", type(e).__name__, "–", e) 
        #     time.sleep(5)
        #     return [];

