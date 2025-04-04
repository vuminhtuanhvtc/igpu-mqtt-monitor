FROM debian:buster-slim

LABEL maintainer="Tuan Vu <vuminhtuanhvtc@gmail.com>"
LABEL description="Monitor Intel iGPU usage and push to Home Assistant via MQTT"

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add non-free repository for intel-gpu-tools
RUN echo "deb http://deb.debian.org/debian buster main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security buster/updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian buster-updates main contrib non-free" >> /etc/apt/sources.list

# Install other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    intel-gpu-tools \
    python3 \
    python3-pip \
    procps \
    pciutils \
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
