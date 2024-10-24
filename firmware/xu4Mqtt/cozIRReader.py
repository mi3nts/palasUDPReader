
#
import serial
import datetime
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
import time
import re

import sys

# Based on https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/2433/CozIR-A%20Data%20Sheet%20Rev%204.4.pdf?_gl=1*1nab7ce*_up*MQ..&gclid=CjwKCAjwtqmwBhBVEiwAL-WAYQRqjE1UBgrvfW2jrsM1j-nJ7-PI5OQRqYQ3tWSDYkmZwsPiYiQkXBoCa8EQAvD_BwE
#  Set auto calibration 
##  Set calibration interval
##  Set Averaging intervals
##  
# Setting Altitude compensation based on UTD COordinates - Setting it to 200 m



dataFolderReference    = mD.dataFolderReference
portIn                 = "/dev/ttyS0"
baudRate               = 9600

# May change depending on location
expectedAltitude       = 200;
loopInterval           = 1 
def main(portNum):

    menuSetUp = False
    # print(altitude_compensation_string(expectedAltitude))

    ser = serial.Serial(
    port= portIn,\
    baudrate=baudRate,\
	parity  =serial.PARITY_NONE,\
	stopbits=serial.STOPBITS_ONE,\
	bytesize=serial.EIGHTBITS,\
    timeout=0)

    print(" ")
    print("Connected to: " + ser.portstr)
    print(" ")
    line = []

    print("Setting the sensor into polling mode")
    ser.write(str.encode('K 2\r\n'))
    time.sleep(1)

    
    setupDone  = False; 
    
    
    while True:
        try:
            for c in ser.read():
                line.append(chr(c))
                if chr(c) == '\n' and not(menuSetUp):
                    dataString = ''.join(line)
                    dataString     = (''.join(line)).replace("\n","").replace("\r","")
                    # print("Setting COZIR Sensor")
                    # print("Setting the sensor into polling mode")
                    # ser.write(str.encode('K 2\r\n'))
                    # time.sleep(1)
                    
                    print("Setting COZIR to emit all data")
                    ser.write(str.encode('M 04166\r\n'))
                    time.sleep(1)

                    # print("Asking for Data")
                    # ser.write(str.encode('Q\r\n'))
                    # time.sleep(1)

                    print("Reading the altitude compensation value")
                    ser.write(str.encode('s\r\n'))
                    time.sleep(1)

                    print("Setting Compensation Value")
                    ser.write(str.encode(altitude_compensation_string(expectedAltitude)))
                    time.sleep(1)
                    
                    print("Reading the altitude compensation value")
                    ser.write(str.encode('s\r\n'))
                    time.sleep(1)

                    print("Reading the auto zero value")
                    ser.write(str.encode('@\r\n'))
                    time.sleep(1)
                    # Make sure that it returns @1.08.0

                    # print("Turning the auto zero value off")
                    # ser.write(str.encode('@ 0\r\n'))
                    # time.sleep(1)

                    # print("Reading the auto zero value")
                    # ser.write(str.encode('@\r\n'))
                    # time.sleep(1)

                    # print("Setting the auto zero value")
                    # ser.write(str.encode('@ 1.0 8.0\r\n'))
                    # time.sleep(1)

                    # print("Reading the auto zero value")
                    # ser.write(str.encode('@\r\n'))
                    # time.sleep(1)
                    # According to climate.gov (https://www.climate.gov/news-features/understanding-climate/climate-change-atmospheric-carbon-dioxide)
                    # the lowest atmospheric co2 levels is 418.5 ppm 
                    # As such setting the auto zero co2 level as 418.0 

                    # This has to be added for the final code 
                    print("Setting the value of auto calibration")
                    ser.write(str.encode('P 8 1\r\n'))
                    time.sleep(1)
                    ser.write(str.encode('P 9 162\r\n'))
                    time.sleep(1)

                    print("Reading the digital filter value")
                    ser.write(str.encode('a\r\n'))
                    time.sleep(1)

                    # print("Asking for Data")
                    # ser.write(str.encode('Q\r\n'))
                    # time.sleep(1)

                    print("Setting the sensor into Streaming mode")
                    ser.write(str.encode('K 1\r\n'))
                    time.sleep(1)

                    menuSetUp = True
                    line = []

                if chr(c) == '\n' and (menuSetUp):
                    # dateTime = datetime.datetime.now()
                    dataStringPost     = (''.join(line)).replace("\n","").replace("\r","").replace(" ","")
                    # print(dataStringPost)
                    line = []
                    if check_format(dataStringPost):
                        mSR.COZIRAEH2000Write((decode_cozir_data(dataStringPost)))
                        # ser.write(str.encode('Q\r\n'))
                    time.sleep(.1)

                     

        except Exception as e:
            print(f"Incomplete read. Something may be wrong with {portIn}: {e}")
            line = []

   
def altitude_compensation_string(altitude):
    cv = compensation_value(altitude)
    print("Compensation Value: ")
    print(cv)
    setString  = "S "+ str(round(cv)) + "\r\n"
    return setString
    

def check_format(s):
    """
    Check if the string has the format 'H ddddd T ddddd Z ddddd z ddddd'.
    
    :param s: The string to check.
    :return: True if the string matches the format, False otherwise.
    """
    pattern = r'^H\d{5}T\d{5}Z\d{5}z\d{5}$'
    match   = re.match(pattern, s)
    return bool(match)

def decode_cozir_data(data):
    """
    Decodes COZIR sensor data from a formatted string.
    :param data: The string containing the sensor data.
    :return: A dictionary with decoded values.
    """
    print(data)
    try:     
        dateTime      = datetime.datetime.now()
        humidity      = int(data[1:6]) / 10.0             # Assuming the humidity is given in tenths of percentage
        temperature   = (int(data[7:12]) - 1000) / 10.0   # Assuming the temperature is given in tenths of degrees Celsius
        co2Filtured   = int(data[13:18])                  # CO2 concentration in ppm
        co2Recent     = int(data[19:])                    # Another CO2 concentration in ppm or another parameter
        return [dateTime,co2Recent,co2Filtured,temperature,humidity]
    
    except (IndexError, ValueError) as e:
        print(f"Error decoding data: {e}")
        return None

# def sea_level_difference(meters):
#     return (0.0316)*meters_to_feet(meters)

# # def compensation_value(meters):
# #     return 8192+ ((sea_level_difference(meters)*.14)/100)*8192

# def meters_to_feet(meters):
#     feet_per_meter = 3.280839895013123
#     feet = meters * feet_per_meter
#     return feet

def compensation_value(altitude_m):
    """
    Calculate the compensation value based on the altitude in meters.

    Parameters:
    altitude_m (float): Altitude in meters.

    Returns:
    float: Compensation value.
    """
    base_value = 8192  # Base compensation value
    coefficient = 1.35  # Coefficient derived from the sea level difference formula
    return base_value + coefficient * altitude_m



if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print("Monitoring COZIR Sensor on port: {0}".format(portIn)+ " with baudrate " + str(baudRate))
    main(portIn)