#!/bin/bash

echo "Starting Intel iGPU MQTT Monitor..."
echo "MQTT Host: ${MQTT_HOST:-localhost}"
echo "MQTT Port: ${MQTT_PORT:-1883}"
echo "Update Interval: ${MQTT_UPDATE_INTERVAL:-5} seconds"

# Check architecture
ARCH=$(uname -m)
if [ "$ARCH" != "x86_64" ]; then
    echo "ERROR: This container is designed to run on x86_64 architecture only."
    echo "Current architecture: $ARCH"
    exit 1
fi

# Check if intel_gpu_top is installed
if ! command -v intel_gpu_top &> /dev/null; then
    echo "ERROR: intel_gpu_top command not found. Please ensure intel-gpu-tools is installed."
    exit 1
fi

# Check if GPU devices are available
if [ ! -e /dev/dri ]; then
    echo "ERROR: GPU devices not found. Make sure /dev/dri is mapped correctly."
    exit 1
fi

# Run the monitor script
exec python3 /app/mqtt_igpu_monitor.py
