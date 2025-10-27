#!/bin/bash
# Simple wrapper to run the Python FIM and log results

LOGFILE="/home/ovi/Documents/fim/fim_log.txt"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$TIMESTAMP] Running file integrity check..." >> "$LOGFILE"
python3 /home/ovi/Documents/fim/fim_check.py >> "$LOGFILE" 2>&1
echo "----------------------------------------" >> "$LOGFILE"

