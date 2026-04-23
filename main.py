import paho.mqtt.client as mqtt
import datetime
import json
import random
import string
import threading
import argparse
from gps_sensor import TinkerforgeGPSSensor, SimulatedGPSSensor, run_gps
from dht11_worker import DHT11Sensor, SimulatedDHT11Sensor, run_dht11
from light_sensor import RealLightSensor, SimulatedLightSensor, run_light_sensor
from sound import RealSoundSensor, SimulatedSoundSensor, run_sound_sensor

HOST = "localhost"
MQTT_PORT = 1883

def build_client():
    random_client_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    client = mqtt.Client(client_id = "RPi3-"+random_client_name, clean_session=True, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    def on_connect(client, userdata, flags, rc, properties = None):
        if rc == 0:
            print("Connection successful ")
            client.subscribe("SRH/#")
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
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect #assigning function objects to callbacks
    return client

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation", action="store_true", help="Run in simulation mode")
    args = parser.parse_args()

    if args.simulation:
        print("Running in simulation mode")
        gps_sensor = SimulatedGPSSensor()
        temp_sensor = SimulatedDHT11Sensor()
        light_sensor = SimulatedLightSensor()
        sound_sensor = SimulatedSoundSensor()

    else:
        print("Running in live mode")
        gps_sensor = TinkerforgeGPSSensor()
        temp_sensor = DHT11Sensor()
        light_sensor = RealLightSensor()
        sound_sensor = RealSoundSensor()

    client = build_client()

    threads = [
        threading.Thread(target=run_dht11, args=(client, temp_sensor), daemon=True),
        threading.Thread(target=run_light_sensor, args=(client, light_sensor), daemon=True),
        threading.Thread(target=run_sound_sensor, args=(client, sound_sensor), daemon=True),
        threading.Thread(target=run_gps, args=(client, gps_sensor), daemon=True),  
    ]

    for thread in threads:
        thread.start()

    client.connect(host=HOST, port=MQTT_PORT)

    client.loop_forever()

if __name__ == "__main__":
    main()