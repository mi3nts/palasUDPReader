# Import tkinter and webview libraries
# from fileinput import filename
# # from tkinter import *
# from traceback import print_stack
# import webview
import glob
import serial
import datetime
import traceback
# from mintsXU4 import mintsSensorReader as mSR
# from mintsXU4 import mintsDefinitions as mD
import time
# import serial
# import pynmea2
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
# import mintsLatest as mL
import csv
import os 
# import nmap, socket
import yaml
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS 

import sys
import yaml
import os
import time
import glob
from collections import defaultdict
import pandas as pd
import re
import socket
import math
from datetime import date, timedelta, datetime
from mintsXU4 import mintsDefinitions as mD

# This will run continously

# Steps 
#   1) Collects all csvs it can find 
#   2) For each csv it checks if it has already synced - 
#          Do this using a nested yaml file with sensor ID @ mintsData/ID/id_influxUpdated.yaml

#   It checks if the sensor has internet 

#  With on board sensors:
    # Node ID should be updated 
    # Some means to check if connectivity is there 
    # How long should I go back to 
    # How often to send 
    # Check if already synced 

# nodeInfo         = mD.nodeInfo
# sensorInfo       = mD.sensorInfo

# nodeInfo         = pd.read_csv('https://raw.githubusercontent.com/mi3nts/AirQualityAnalysisWorkflows/main/influxdb/nodered-docker/id_lookup.csv')
# sensorInfo       = pd.read_csv('https://raw.githubusercontent.com/mi3nts/mqttSubscribersV2/main/lists/sensorIDs.csv')

dataFolder         = mD.dataFolder

nodeID             = mD.macAddress 
dataFileInflux     = dataFolder + "/" + nodeID + "/" + nodeID + ".yaml"

# sensorIDs          = sensorInfo['sensorID']
credentials        = mD.credentials

influxToken        = credentials['influx']['token']  
influxOrg          = credentials['influx']['org'] 
influxBucket       = credentials['influx']['bucket'] 
influxURL          = credentials['influx']['url']

batchSize          = 500

print()
print("MINTS")
print()

delta      = timedelta(days=1)

# Check every 5 minutes
loopTime   =  300


def directoryCheckV2(outputPath):
    isFile = os.path.isfile(outputPath)
    if isFile:
        return True
    if outputPath.find(".") > 0:
        directoryIn = os.path.dirname(outputPath)
    else:
        directoryIn = os.path.dirname(outputPath+"/")

    if not os.path.exists(directoryIn):
        print("Creating Folder @:" + directoryIn)
        os.makedirs(directoryIn)
        return False
    return True;


def isFloat(value):
    # When its a an empty value - Send a string
    # 
    
    try:
        if value.strip() == '':
            return None

        output = float(value)

        return output
    except Exception as e:
        return value

def parse_csv_filename(filename):
    # Define a regex pattern to extract parameters
    pattern = re.compile(r'^(\w+)_(\w+)_(\w+)_(\d{4})_(\d{2})_(\d{2})\.csv$')
    # filename = os.path.basename(path)
    # Match the pattern against the filename
    match = pattern.match(os.path.basename(filename))
    if match:
        # Extract matched groups
        device_type = match.group(1)
        mac_address = match.group(2)
        sensorID  = match.group(3)
        year = match.group(4)
        month = match.group(5)
        day = match.group(6)
        fileDate = datetime(year=int(year), month=int(month), day=int(day)).date()
        return sensorID, fileDate
    else:
        raise ValueError(f"Filename {filename} does not match the expected pattern.")


def syncData2Influx(nodeID,nodeName):

    today = datetime.now().date()
    # print(today)
    # print(dataFolder  + "/" + nodeID + "/" + "/*/*/*/*"+sensorID+"*.csv")
    csvDataFiles = glob.glob(\
                    dataFolder  + "/" +  nodeID + "/*/*/*/*"+nodeID+"*.csv")
    csvDataFiles.sort()

    # At this point this should check if the data is from today or not 
    # If its not today you sync it and record it 
    # If its today you record the last point - Every time the code starts 
    # again witin a while loop you check for a new time  

    for csvFile in csvDataFiles:
        # print(csvFile)
        sensorID, fileDate = parse_csv_filename(csvFile)      
        if sensorID is not None:
            if fileDate != today: 
                # print(fileDate)
                # print("================================================")
                # print("Syncing "+ csvFile)
                sendCSV2Influx(csvFile,nodeID,sensorID,nodeName,fileDate)
            else:
                sendCSV2InfluxToday(csvFile,nodeID,sensorID,nodeName,fileDate)

def writeJSONInfluxLatest(dateTime,sensorID):
    directoryIn  = dataFolder+"/"+nodeID+"/"+sensorID+"_influx_sync.json"
    print(directoryIn)

    dateTimeStr = dateTime.isoformat()
    # Add a directory check 
    try:
        with open(directoryIn, 'w') as json_file:
            json.dump(dateTimeStr, json_file, indent=4)
    except:
        print("Json Data Not Written")



def readJSONInfluxLatest(sensorID):
    directoryIn  = dataFolder+"/"+nodeID+"/"+sensorID+"_influx_sync.json"
    # print(directoryIn)
    # # Add a directory check 

    try:
        with open( directoryIn, 'r') as json_file:
            datetime_str = json.load(json_file)

        # Convert the string back to a datetime object
        dateTimeRead = datetime.fromisoformat(datetime_str)
        return dateTimeRead
    except:
    
        print("Json Data Not Written")
        return datetime(1970, 1, 1, 0, 0, 0)
       

def sendCSV2InfluxToday(csvFile,nodeID,sensorID,nodeName,fileDate):
    print()
    print("--------------")
    print("send CSV2 Influx Today")
    print(csvFile)
    time.sleep(1)
    try:
        if not is_connected():
            print("No Connectivity")
            return 
        
        sequence = []
        tag_columns  = ["device_id", "device_name"]
        time_column  = "dateTime"
        lastDateTime = readJSONInfluxLatest(sensorID)


        with open(csvFile, "r") as f:
            reader            = csv.DictReader((line.replace('\0','') for line in f) )
            rowList           = list(reader)
            for i, rowData in enumerate(rowList):
                try:
                    dateTimeRow = datetime.strptime(rowData['dateTime'], '%Y-%m-%d %H:%M:%S.%f')

                        # print(rowData)
                    # print(lastDateTime)
                    # print(dateTimeRow)
                    # print(lastDateTime<dateTimeRow)
                    if lastDateTime<dateTimeRow:
                        if sensorID == "BME280" or sensorID == "BME680":
                            # print(rowData)
                            if float(rowData["humidity"]) > 0:
                                rowData["dewPoint"] = str(243.04 * (math.log(float(rowData["humidity"]) / 100.0) + ((17.625 * float(rowData["temperature"])) / (243.04 + float(rowData["temperature"])))) \
                                    / (17.625 - math.log(float(rowData["humidity"]) / 100.0) - ((17.625 * float(rowData["temperature"])) / (243.04 + float(rowData["temperature"])))))
                            else:
                                rowData["dewPoint"] = str(0)
                        # print(lastDateTime)
                        # print(dateTimeRow)
                        # print(lastDateTime<dateTimeRow)
                        # print("New Live data found")
                        point = Point(sensorID)
                        point.tag("device_id", nodeID)
                        point.tag("device_name", nodeName)
                        point.time(dateTimeRow, WritePrecision.NS)
                        for header in reader.fieldnames:
                            if header not in tag_columns and header != time_column:
                                if sensorID == "MWBR001" and header == "rtcTime":
                                    point.field(header, float(dateTimeRow.year))
                                else:
                                    point.field(header, isFloat(rowData[header]))
                        sequence.append(point)
                except Exception as e:
                    print(f"-- An error occurred --: {e}")
                    traceback.print_exc()

                # print(len(sequence))
                # len(sequence) > 0
                if ((i + 1) % batchSize == 0 or i == len(rowList) - 1) and len(sequence) > 0 :
                    try:
                        # print(len(sequence))
                        # len(sequence) > 0
                        print(i+1)
                        with InfluxDBClient(url=influxURL, token=influxToken, org=influxOrg) as client:
                            write_api = client.write_api(write_options=SYNCHRONOUS)
                            write_api.write(influxBucket, influxOrg, sequence)
                        sequence.clear()
                        time.sleep(.25)

                    except Exception as e:
                        print(f"-- An error occurred --: {e}")
                        traceback.print_exc()
                        sequence.clear()

        if not is_connected():
            print("No Connectivity")
            return False;

        writeJSONInfluxLatest(dateTimeRow,sensorID)

        return True; 

    except Exception as e:
        print(rowData)
        print(f"An error occurred: {e}")
   

def sendCSV2Influx(csvFile,nodeID,sensorID,nodeName,fileDate):
    print()
    print("--------------")
    print("sendCSV2Influx")
    print(csvFile)


    try:
    # while True:

        # print(csvFile)
        if not is_connected():
            print("No Connectivity")
            return 
        
        sequence = []
        tag_columns = ["device_id", "device_name"]
        time_column = "dateTime"
        currentRecord = read_records(dataFileInflux)
        fileDateStr = str(fileDate.strftime('%Y-%m-%d'))

        if check_id_date_exists(sensorID, fileDateStr, currentRecord, dataFileInflux):
            print("File already synced")
            print()
            return; 
        # At this point I need the date from the csv file 
        # print(currentRecord)

        with open(csvFile, "r") as f:
            reader            = csv.DictReader((line.replace('\0','') for line in f) )
            rowList           = list(reader)
            for i, rowData in enumerate(rowList):
                try:
                    dateTimeRow = datetime.strptime(rowData['dateTime'], '%Y-%m-%d %H:%M:%S.%f')

                    if sensorID == "BME280" or sensorID == "BME680":
                        # print(rowData)
                        if float(rowData["humidity"]) > 0:
                            rowData["dewPoint"] = str(243.04 * (math.log(float(rowData["humidity"]) / 100.0) + ((17.625 * float(rowData["temperature"])) / (243.04 + float(rowData["temperature"])))) \
                                / (17.625 - math.log(float(rowData["humidity"]) / 100.0) - ((17.625 * float(rowData["temperature"])) / (243.04 + float(rowData["temperature"])))))
                        else:
                            rowData["dewPoint"] = str(0)

                    point = Point(sensorID)
                    point.tag("device_id", nodeID)
                    point.tag("device_name", nodeName)
                    point.time(dateTimeRow, WritePrecision.NS)
                    for header in reader.fieldnames:
                        if header not in tag_columns and header != time_column:
                            if sensorID == "MWBR001" and header == "rtcTime":
                                point.field(header, float(dateTimeRow.year))
                            else:
                                point.field(header, isFloat(rowData[header]))
                    sequence.append(point)
                except Exception as e:
                    print(f"-- An error occurred --: {e}")
                    traceback.print_exc()

                
                if (i + 1) % batchSize == 0 or i == len(rowList) - 1:
                    try:
                        print(i+1)
                        with InfluxDBClient(url=influxURL, token=influxToken, org=influxOrg) as client:
                            write_api = client.write_api(write_options=SYNCHRONOUS)
                            write_api.write(influxBucket, influxOrg, sequence)
                        sequence.clear()
                        time.sleep(.25)

                    except Exception as e:
                        print(f"-- An error occurred --: {e}")
                        traceback.print_exc()
                        sequence.clear()


        if not is_connected():
            print("No Connectivity")
            return False;

        print("Record ID Date")
        record_id_date(sensorID, date=str(fileDate), \
                        filename=dataFileInflux) # Name should be updated 

        return True; 

    except Exception as e:
        # print(rowData)
        print(point)
        print(f"An error occurred: {e}")
        traceback.print_exc()

# Load existing records or create a new structure
def load_records(filename='id_date_records.yaml'):
    try:
        with open(filename, 'r') as file:
            records = yaml.safe_load(file) or {}
    except Exception as e:
        records = {}
    return records

# Save records to the YAML file
def save_records(records, filename='id_date_records.yaml'):
    with open(filename, 'w') as file:
        yaml.safe_dump(dict(records), file)


# Read and print all records
def read_records(filename='id_date_records.yaml'):
    records = load_records(filename)
    for id_value, dates in records.items():
        print(f"ID: {id_value}")
        for date in dates:
            print(f"  Date: {date}")


# Add a new date to an ID record, with an optional custom date
def record_id_date(id_value, date=None, filename='id_date_records.yaml'):
    records = load_records(filename)
    # print(records)

    # Ensure the structure is a defaultdict of lists for easier management
    records = defaultdict(list, records)
    # print(records)
    
    # Use the provided date or the current date (without time) if not provided
    if date is None:
        date = str(datetime.now().strftime('%Y-%m-%d'))
    # print(records)

    # Check if the ID and date combination already exists
    if check_id_date_exists(id_value, date, records):
        print(f"ID={id_value} with Date={date} already exists.")
        return
    
    # Add the date to the list of dates for this ID
    records[id_value].append(date)
    # print(records)


    save_records(records, filename)
    print(records)

    print(f"Recorded: ID={id_value}, Date={date}")


# Check if a specific ID and date combination exists
def check_id_date_exists(id_value, date, records=None, filename='id_date_records.yaml'):

    if records is None:
        records = load_records(filename)


    # Check if the ID exists and the date is in the list for that ID
    if id_value in records and date in records[id_value]:
        return True
    return False

# Read and print all records
def read_records(filename='id_date_records.yaml'):
    records = load_records(filename)
    # for id_value, dates in records.items():
    #     print(f"ID: {id_value}")
    #     for date in dates:
    #         print(f"  Date: {date}")
    return records;

def getNodeName(nodeID):
    try:
        nodeInfo           = pd.read_csv('https://raw.githubusercontent.com/mi3nts/AirQualityAnalysisWorkflows/main/influxdb/nodered-docker/id_lookup.csv')
        nodeIDs            = nodeInfo['mac_address']
        nodeNames          = nodeInfo['name']
        matchingIndex = list(nodeIDs).index(nodeID)
        nodeName= nodeNames[matchingIndex]
        return nodeName
    except Exception as e:
        return None

def delayMintsV2(startTime,loopTime):
    currentTime = time.time() 
    timeSpent   = currentTime - startTime 
    if(loopTime>timeSpent):
        waitTime = loopTime - timeSpent;
        print("Sleeping for " +str(waitTime) +  " seconds")
        time.sleep(waitTime);
    return currentTime;


def is_connected(hostname="www.google.com"):
    try:
        # Connect to the host -- tells us if the host is actually reachable
        socket.create_connection((hostname, 80), 2)
        return True
    except Exception as e:
        return False

def main():    
    # At this point just check for the node name via internet 
    syncTime = time.time()
    while True:
        try:
            if is_connected():
                nodeName = getNodeName(nodeID)
                if nodeName is not None:
                    syncData2Influx(nodeID,nodeName)
                    syncTime = delayMintsV2(syncTime,loopTime)             
            else:
                print("Sleeping for 1 minute")
                time.sleep(60)
                

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    main()