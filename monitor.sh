#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Error: Expected 2 arguments, but got $#."
    echo "Usage: $0 <log_file> <server_ip>"
    exit 1
fi

LOG_FILE=$1
SERVER=$2

# Initialize the log file
truncate -s 0 "$LOG_FILE"

# Infinite loop to log socket stats
while true; do
    ss -ein dst "$SERVER" | ts '%.s' >> "$LOG_FILE" 2>/dev/null
    sleep 0.1
done
