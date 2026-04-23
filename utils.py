import json
import os

DEFAULT_CONFIG = {
    "temperature": {"min": 18, "max": 30},
    "humidity":    {"min": 30, "max": 70}
}

def load_config(path="config.json"):
    if not os.path.exists(path):
        print(f"[WARNING] Config file '{path}' not found, using defaults")
        return DEFAULT_CONFIG
    with open(path) as f:
        return json.load(f)

def publish_message(client, sensor, fields, timestamp):
    data = {
        "time": timestamp,
        "measurement": sensor,
        "tags": {
            "location": "server-room-1"
        },
        "fields": fields
    }

    try:
        client.publish(f"SRH/RPi3/{sensor}/msg", payload = json.dumps(data))
    except Exception as e:
        print(f"Error: {e}")