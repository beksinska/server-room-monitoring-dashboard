#import RPi.GPIO as GPIO
import time
from abc import ABC, abstractmethod

BUZZER_PIN = 18 
VIBRATION_PIN = 27

class Warning(ABC):
    @abstractmethod
    def run_warning(self):
        pass

class GPIOWarning(Warning):
    def __init__(self, buzzer_pin=BUZZER_PIN, vibration_pin=VIBRATION_PIN):
        import RPi.GPIO as GPIO
        self._GPIO = GPIO
        self.buzzer_pin = buzzer_pin
        self.vibration_pin = vibration_pin

        if not self._GPIO.getmode():
            self._GPIO.setmode(self._GPIO.BCM)

        self._GPIO.setup(self.buzzer_pin, self._GPIO.OUT)
        self._GPIO.setup(self.vibration_pin, self._GPIO.OUT)

    def run_warning(self):
        try:
            self._GPIO.output(self.buzzer_pin, self._GPIO.HIGH)
            self._GPIO.output(self.vibration_pin, self._GPIO.HIGH)
            time.sleep(1)
            self._GPIO.output(self.buzzer_pin, self._GPIO.LOW)
            self._GPIO.output(self.vibration_pin, self._GPIO.LOW)
        except KeyboardInterrupt:
            self._GPIO.output(self.buzzer_pin, self._GPIO.LOW)
            self._GPIO.output(self.vibration_pin, self._GPIO.LOW)

class SimulatedWarning(Warning):
    def run_warning(self):
        print("[SIM] Warning: Threshold exceeded!")
        time.sleep(1)

                
