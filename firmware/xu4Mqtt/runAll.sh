#!/bin/bash

sleep 60

kill $(pgrep -f 'gpsReader.py')
sleep 5
python3 gpsReader.py &
sleep 5

kill $(pgrep -f 'palasUDPReader.py')
sleep 5
python3 palasUDPReader.py &
sleep 5

python3 ipReader.py
sleep 5