import argparse
import paho.mqtt.client as mqtt
import datetime
import json
import influxdb
import random
import string
import threading
#import buzzer 
from warning import GPIOWarning, SimulatedWarning
import os
from dotenv import load_dotenv

load_dotenv()

HOST, PORT = "localhost", 1883 # change HOST to Pi's IP address when using Pi

db = influxdb.InfluxDBClient(host='localhost', port=8086, username='pi', password=os.getenv('INFLUXDB_PASSWORD'))
db.switch_database('RPi3')

def on_connect(client, userdata, flags, rc, properties = None):
    if rc == 0:
        print("Connection successful ")
        client.subscribe("SRH/RPi3/#")
    elif rc == 1:
        print("Connection refused - incorrect protocol version")
    elif rc == 2:
        print("Connection refused - invalid client identifier")
    elif rc == 3:
        print("Connection refused - server unavailable")
    elif rc == 4:
        print("Connection refused - bad username or/and password")
    elif rc == 5:
        print("Connection refused - not authorized")
    else:
        print(f"Connection refused: {rc}")

def on_disconnect(client, userdata, rc, properties = None):
    print(f"Disconnected with {rc}")

def process_message(warning: GPIOWarning):
    def on_message(client, userdata, msg):
        print(f"{msg.topic} -> {msg.payload.decode()}") #the message is binary
        if msg.topic == "SRH/RPi3/warning":
            warning.run_warning()
            return

        sensor_topics = [
            "SRH/RPi3/DHT11/msg",
            "SRH/RPi3/Light/msg",
            "SRH/RPi3/Sound/msg",
            "SRH/RPi3/GPS/msg"
        ]
        if msg.topic in sensor_topics:
            data_json = msg.payload.decode("utf-8")
            data_dict = json.loads(data_json) 
            if not db.write_points([data_dict]):
                print("error writing to InfluxDB")
    
    return on_message

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation", action="store_true", help="Run in simulation mode")
    args = parser.parse_args()

    if args.simulation:
        print("[SIM] Running in simulation mode")
        warning = SimulatedWarning()
    else:
        print("[LIVE] Running in normal mode")
        warning = GPIOWarning()

    random_client_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    client = mqtt.Client(
        client_id="RPi3-" + random_client_name,
        clean_session=True,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.on_message    = process_message(warning)

    client.connect(host=HOST, port=PORT)
    client.loop_forever()


if __name__ == "__main__":
    main()
