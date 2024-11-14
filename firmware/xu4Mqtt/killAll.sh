#!/bin/bash


sleep 5

kill $(pgrep -f 'palasUDPReader.py')
sleep 5

kill $(pgrep -f 'gpsReader.py')
sleep 5

