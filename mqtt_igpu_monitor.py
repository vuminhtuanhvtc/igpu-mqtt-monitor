#!/usr/bin/env python3

import os
import time
import json
import subprocess
import re
import socket
import paho.mqtt.client as mqtt

# Configuration from environment variables
mqtt_host = os.environ.get('MQTT_HOST', 'localhost')
mqtt_port = int(os.environ.get('MQTT_PORT', 1883))
mqtt_username = os.environ.get('MQTT_USERNAME', '')
mqtt_password = os.environ.get('MQTT_PASSWORD', '')
update_interval = int(os.environ.get('MQTT_UPDATE_INTERVAL', 5))

# Get hostname for MQTT discovery
hostname = socket.gethostname()

# Function to get GPU info
def get_gpu_info():
    try:
        # Get GPU information
        gpu_info_cmd = "lspci -nn | grep VGA | grep Intel"
        gpu_info_result = subprocess.check_output(gpu_info_cmd, shell=True, text=True).strip()
        
        # Extract GPU model from the output
        gpu_model = re.search(r"Intel.*\[", gpu_info_result)
        gpu_model = gpu_model.group(0).replace("[", "").strip() if gpu_model else "Intel iGPU"
        
        # Try to get GPU generation information
        try:
            gen_info_cmd = "intel_gpu_top -l 1 | grep -i gen"
            gen_info_result = subprocess.check_output(gen_info_cmd, shell=True, text=True).strip()
            if "Gen" in gen_info_result:
                gpu_gen = re.search(r"Gen\d+", gen_info_result)
                if gpu_gen:
                    gpu_model += f" ({gpu_gen.group(0)})"
        except:
            pass
            
        return gpu_model
    except:
        return "Intel iGPU"

# Function to get GPU usage statistics
def get_gpu_usage():
    try:
        # Run intel_gpu_top with a single iteration
        cmd = "intel_gpu_top -J -s 100 -o - -l 1"
        result = subprocess.check_output(cmd, shell=True, text=True)
        
        # Parse the JSON output
        data = {}
        try:
            # Try parsing the output as JSON
            json_data = json.loads(result)
            
            # Extract the relevant data
            engines = json_data.get('engines', {})
            
            data = {
                'render': engines.get('Render/3D', {}).get('busy', 0),
                'blitter': engines.get('Blitter', {}).get('busy', 0),
                'video': engines.get('Video', {}).get('busy', 0),
                'video_enhance': engines.get('VideoEnhance', {}).get('busy', 0)
            }
        except json.JSONDecodeError:
            # Fallback to regex parsing if JSON parsing fails
            render_match = re.search(r'Render/3D.+?(\d+)%', result)
            blitter_match = re.search(r'Blitter.+?(\d+)%', result)
            video_match = re.search(r'Video.+?(\d+)%', result)
            video_enhance_match = re.search(r'VideoEnhance.+?(\d+)%', result)
            
            data = {
                'render': int(render_match.group(1)) if render_match else 0,
                'blitter': int(blitter_match.group(1)) if blitter_match else 0,
                'video': int(video_match.group(1)) if video_match else 0,
                'video_enhance': int(video_enhance_match.group(1)) if video_enhance_match else 0
            }
            
        return data
    except Exception as e:
        print(f"Error getting GPU usage: {e}")
        return {
            'render': 0,
            'blitter': 0,
            'video': 0,
            'video_enhance': 0
        }

# Setup MQTT
client = mqtt.Client()
if mqtt_username and mqtt_password:
    client.username_pw_set(mqtt_username, mqtt_password)

# Get GPU model
gpu_model = get_gpu_info()
print(f"Detected GPU: {gpu_model}")

# Connect to MQTT broker
try:
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_start()
    print(f"Connected to MQTT broker at {mqtt_host}:{mqtt_port}")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)

# Function to publish Home Assistant auto-discovery config
def publish_config(component, name, unit=None, icon=None, state_topic=None):
    if state_topic is None:
        state_topic = f"homeassistant/sensor/igpu/{component}/state"
    
    config = {
        "name": f"iGPU {name}",
        "unique_id": f"igpu_{component}_{hostname}",
        "state_topic": state_topic,
        "device": {
            "identifiers": [f"igpu_monitor_{hostname}"],
            "name": f"Intel iGPU Monitor ({hostname})",
            "model": gpu_model,
            "manufacturer": "Intel"
        }
    }
    
    if unit:
        config["unit_of_measurement"] = unit
    
    if icon:
        config["icon"] = icon
    
    config_topic = f"homeassistant/sensor/igpu/{component}/config"
    client.publish(config_topic, json.dumps(config), retain=True)
    print(f"Published config for {name}")

# Publish discovery configs
publish_config("render", "Render/3D Usage", "%", "mdi:cube-outline")
publish_config("blitter", "Blitter Usage", "%", "mdi:flash")
publish_config("video", "Video Usage", "%", "mdi:video")
publish_config("video_enhance", "Video Enhance Usage", "%", "mdi:video-plus")
publish_config("model", "Model", None, "mdi:chip", "homeassistant/sensor/igpu/model/state")
client.publish("homeassistant/sensor/igpu/model/state", gpu_model)

print(f"Starting monitoring loop with {update_interval} second intervals")

try:
    while True:
        # Get current usage
        usage = get_gpu_usage()
        
        # Publish values
        client.publish("homeassistant/sensor/igpu/render/state", usage['render'])
        client.publish("homeassistant/sensor/igpu/blitter/state", usage['blitter'])
        client.publish("homeassistant/sensor/igpu/video/state", usage['video'])
        client.publish("homeassistant/sensor/igpu/video_enhance/state", usage['video_enhance'])
        
        time.sleep(update_interval)
except KeyboardInterrupt:
    print("Monitoring stopped")
finally:
    client.loop_stop()
    client.disconnect()
