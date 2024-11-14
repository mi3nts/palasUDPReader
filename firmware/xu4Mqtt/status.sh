#!/bin/bash
#
sleep 1
echo "Palas Frog"
echo $(pgrep -f 'palasUDPReader.py')
sleep 2

echo "GPS"
echo $(pgrep -f 'gpsReader.py')
sleep 2

echo "IP"
echo $(pgrep -f 'ipReader.py')
sleep 2

