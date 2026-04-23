import time
import datetime
import os
import random
from utils import publish_message
from abc import ABC, abstractmethod

# sound_pin wird definiert
SOUND_PIN = 24

class SoundSensor(ABC):
    @abstractmethod
    def read_sound(self):
        pass

class RealSoundSensor(SoundSensor):
    def __init__(self, pin = SOUND_PIN):
        import RPi.GPIO as GPIO
        self._GPIO = GPIO
        self._pin = pin

        # GPIO mode wird auf GPIO.BOARD gesetzt
        if not self._GPIO.getmode():
            self._GPIO.setmode(self._GPIO.BCM)
        self._GPIO.setup(self._pin, self._GPIO.IN, pull_up_down=self._GPIO.PUD_UP) 

    def read_sound(self):
        noise_detected = self._GPIO.input(self._pin) == self._GPIO.LOW
        return 1 if noise_detected else 0
    
class SimulatedSoundSensor(SoundSensor):
    NOISE_PROBABILITY = 0.2

    def read_sound(self):
        return 1 if random.random() < self.NOISE_PROBABILITY else 0
    

def run_sound_sensor(mqtt_client, sensor: SoundSensor):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"sound_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.log")
    while True:
        noise_detected = sensor.read_sound() == 1
        sound_level = 1 if noise_detected else 0
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        log_entry = f"{datetime.datetime.now(datetime.timezone.utc)}, Noise Detected: {noise_detected}\n"
        with open(log_file, "a") as f:
            f.write(log_entry)
        publish_message(
            client=mqtt_client,
            sensor="Sound",
            fields={"sound": sound_level},
            timestamp=timestamp
        )
        time.sleep(1)