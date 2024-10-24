#!/bin/bash

sleep 5

kill $(pgrep -f 'bno080WithPa1010dReader.py')
sleep 1

kill $(pgrep -f 'ips7100Reader.py')
sleep 1

kill $(pgrep -f 'bme280WithTmp117Reader.py')
sleep 1

kill $(pgrep -f 'cozIRReader.py')
sleep 1

kill $(pgrep -f 'piSugarReader.py')
sleep 1

