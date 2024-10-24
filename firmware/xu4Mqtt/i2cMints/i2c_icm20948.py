import smbus2
import time
import datetime
import adafruit_icm20x

class ICM20948:

    def __init__(self, i2c_dev,debugIn):
        
        self.i2c      = i2c_dev
        self.debug    = debugIn


    def initiate(self):
        print("============== ICM20948 ==============")        

        try:
            time.sleep(1)
            self.icm20948  = adafruit_icm20x.ICM20948(self.i2c)
            print("ICM20948 Device Initialized to defauls of +-8g and 500 dps:")
            time.sleep(1)
            return True
        
        except KeyboardInterrupt:
            return False

        except Exception as e:
            time.sleep(5)
            print("An exception occurred:", type(e).__name__, "–", e) 
            time.sleep(5)
            print("ICM20948 Not Found")
            return False 
      
    
    def read(self):
        try:
            dateTime = datetime.datetime.now() 
            self.acceleration =  self.icm20948.acceleration
            self.gyro         =  self.icm20948.gyro
            self.magnetic     =  self.icm20948.magnetic

            return [dateTime,
                    self.acceleration[0],
                    self.acceleration[1],
                    self.acceleration[2],
                    self.gyro[0],
                    self.gyro[1],
                    self.gyro[2],
                    self.magnetic[0],
                    self.magnetic[1],
                    self.magnetic[2]]
        
        except Exception as e:
        
            time.sleep(1)
            print("An exception occurred:", type(e).__name__, "–", e) 
            return [];
        
