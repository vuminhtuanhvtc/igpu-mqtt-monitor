FROM ubuntu:22.04-slim

LABEL maintainer="Tuan Vu <vuminhtuanhvtc@gmail.com>" 
LABEL description="Monitor Intel iGPU usage and push to Home Assistant via MQTT"

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install common dependencies first
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    procps \
    pciutils \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Intel GPU tools (latest version)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common && \
    add-apt-repository ppa:oibaf/graphics-drivers && \
    apt-get update && \
    apt-get install -y --no-install-recommends intel-gpu-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir paho-mqtt typing_extensions

# Create app directory
WORKDIR /app

# Copy Python script
COPY mqtt_igpu_monitor.py /app/
COPY entrypoint.sh /app/

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
