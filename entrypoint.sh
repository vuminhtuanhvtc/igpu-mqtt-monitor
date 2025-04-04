#!/bin/bash

echo "Starting Intel iGPU MQTT Monitor..."
echo "MQTT Host: ${MQTT_HOST:-localhost}"
echo "MQTT Port: ${MQTT_PORT:-1883}"
echo "Update Interval: ${MQTT_UPDATE_INTERVAL:-5} seconds"

# Check if GPU devices are available
if [ ! -e /dev/dri ]; then
    echo "ERROR: GPU devices not found. Make sure /dev/dri is mapped correctly."
    exit 1
fi

# Run the monitor script
exec python3 /app/mqtt_igpu_monitor.py
