#import RPi.GPIO as GPIO
#import dht11
import datetime, time, json, os, random
from utils import publish_message
from abc import ABC, abstractmethod

if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)

    TEMP_MAX = config["temperature"]["max"]
    HUM_MAX = config["humidity"]["max"]
    TEMP_MIN = config["temperature"]["min"]
    HUM_MIN = config["humidity"]["min"]

# Define an abstract base class for temperature sensor
class TemperatureSensor(ABC):
    @abstractmethod
    def read(self):
        pass

# Implement the DHT11 sensor class
class DHT11Sensor(TemperatureSensor):
    def __init__(self):
        import dht11
        import RPi.GPIO as GPIO

        # initialize GPIO
        GPIO.setwarnings(False)
        if not GPIO.getmode():
            GPIO.setmode(GPIO.BCM)

        self._sensor = dht11.DHT11(pin = 4)

    def read(self):
        result = self._sensor.read() # calls the dht11 library's read method
        while not result.is_valid():
            result = self._sensor.read()
        return result.temperature, result.humidity
    
# Implement a simulated sensor 
class SimulatedDHT11Sensor(TemperatureSensor):
    BASE_TEMP = 22.0
    BASE_HUM = 45.0

    def read(self):
        temp = self.BASE_TEMP + random.uniform(-1.0, 1.0)
        hum = self.BASE_HUM + random.uniform(-2.0, 2.0)
        return round(temp, 1), round(hum, 1)

def run_dht11(mqtt_client, sensor: TemperatureSensor):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"gps_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.log")
    while True:
        temp, hum = sensor.read()
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        log_entry = f"{datetime.datetime.now(datetime.timezone.utc)}, Temperature: {temp} degree C, Humidity: {hum}%\n"
        with open(log_file, "a") as f:
            f.write(log_entry)
        publish_message(
            client=mqtt_client,
            sensor="DHT11",
            fields={"temperature": temp, "humidity": hum},
            timestamp=timestamp
        )
        if temp > TEMP_MAX or temp < TEMP_MIN or hum > HUM_MAX or hum < HUM_MIN:
            mqtt_client.publish("SRH/RPi3/warning", "Warning!")
        time.sleep(1)