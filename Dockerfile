FROM debian:buster-slim

LABEL maintainer="vmtuan vuminhtuanhvtc@gmail.com"
LABEL description="Monitor Intel iGPU usage and push to Home Assistant via MQTT"

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    intel-gpu-tools \
    python3 \
    python3-pip \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir paho-mqtt

# Create app directory
WORKDIR /app

# Copy Python script
COPY mqtt_igpu_monitor.py /app/
COPY entrypoint.sh /app/

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
