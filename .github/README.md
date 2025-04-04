# iGPU MQTT Monitor

A lightweight Docker container for monitoring Intel iGPU usage and publishing metrics to Home Assistant via MQTT.

## Features

- Monitors Intel iGPU usage metrics:
  - Render/3D engine usage
  - Blitter engine usage
  - Video engine usage
  - Video Enhancement engine usage
- Automatically creates sensors in Home Assistant via MQTT discovery
- Lightweight Debian-based container
- Easy configuration via environment variables

## Requirements

- Docker
- Intel iGPU (tested with N100 and other Intel processors with integrated graphics)
- MQTT broker (such as the one included with Home Assistant)
- Docker host with access to the iGPU

## Usage

### Docker Compose (Recommended)

```yaml
version: '3'

services:
  igpu-mqtt-monitor:
    container_name: igpu-mqtt-monitor
    image: vmtuan/igpu-mqtt-monitor:latest
    restart: unless-stopped
    privileged: true  # Required to access GPU hardware
    environment:
      - MQTT_HOST=homeassistant.local
      - MQTT_PORT=1883
      - MQTT_USERNAME=your_mqtt_username  # Leave empty if no auth required
      - MQTT_PASSWORD=your_mqtt_password  # Leave empty if no auth required
      - MQTT_UPDATE_INTERVAL=5
    volumes:
      - /dev/dri:/dev/dri  # Access to GPU devices
```

### Docker Run

```bash
docker run -d \
  --name igpu-mqtt-monitor \
  --restart unless-stopped \
  --privileged \
  -e MQTT_HOST=homeassistant.local \
  -e MQTT_PORT=1883 \
  -e MQTT_USERNAME=your_mqtt_username \
  -e MQTT_PASSWORD=your_mqtt_password \
  -e MQTT_UPDATE_INTERVAL=5 \
  -v /dev/dri:/dev/dri \
  vmtuan/igpu-mqtt-monitor:latest
```

## Configuration

The following environment variables can be used to configure the container:

| Variable | Description | Default |
|----------|-------------|---------|
| `MQTT_HOST` | MQTT broker hostname or IP | `localhost` |
| `MQTT_PORT` | MQTT broker port | `1883` |
| `MQTT_USERNAME` | MQTT username (if authentication is required) | `` |
| `MQTT_PASSWORD` | MQTT password (if authentication is required) | `` |
| `MQTT_UPDATE_INTERVAL` | Update interval in seconds | `5` |

## Home Assistant Integration

The container automatically creates sensors in Home Assistant using MQTT discovery. The following sensors will be available:

- iGPU Render/3D Usage (%)
- iGPU Blitter Usage (%)
- iGPU Video Usage (%)
- iGPU Video Enhance Usage (%)
- iGPU Model (displays the detected iGPU model/generation)

No additional configuration is needed in Home Assistant configuration files.

## Building the Image Locally

If you want to build the Docker image locally:

```bash
git clone https://github.com/vuminhtuanhvtc/igpu-mqtt-monitor.git
cd igpu-mqtt-monitor
docker build -t igpu-mqtt-monitor .
```

## Troubleshooting

### No GPU Device Found

If you see an error message about missing GPU devices, make sure:

1. Your host system has an Intel iGPU
2. You've mapped the `/dev/dri` directory correctly
3. The container is running with `--privileged` flag

### Cannot Connect to MQTT

Check that:

1. Your MQTT broker is running and accessible
2. The MQTT host and port are correct
3. If your MQTT broker requires authentication, you've provided the correct username and password

## License

MIT License
