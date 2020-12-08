#!/bin/bash
python3 drowsiness_yawn_invdo_new_condition.py > log &
sleep 2s
sudo python3 data_push_new.py 
