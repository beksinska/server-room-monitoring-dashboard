#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Matt Hawkins
# Author's Git: https://bitbucket.org/MattHawkinsUK/
# Author's website: https://www.raspberrypi-spy.co.uk
# class LightSensor changed and run_light_sensor function added by Daria

#import RPi.GPIO as GPIO
#import smbus
import random
import time
import datetime
import os
from utils import publish_message
from abc import ABC, abstractmethod


class LightSensor(ABC):
    @abstractmethod
    def read_light(self):
        pass

class RealLightSensor(LightSensor):

    def __init__(self):

        import RPi.GPIO as GPIO
        import smbus

        if(GPIO.RPI_REVISION == 1):
            self._bus = smbus.SMBus(0)
        else:
            self._bus = smbus.SMBus(1)
        # Definiere Konstante vom Datenblatt

        self.DEVICE = 0x5c # Standart I2C Geräteadresse

        self.POWER_DOWN = 0x00 # Kein aktiver zustand
        self.POWER_ON = 0x01 # Betriebsbereit
        self.RESET = 0x07 # Reset des Data registers

        # Starte Messungen ab 4 Lux.
        self.CONTINUOUS_LOW_RES_MODE = 0x13
        # Starte Messungen ab 1 Lux.
        self.CONTINUOUS_HIGH_RES_MODE_1 = 0x10
        # Starte Messungen ab 0.5 Lux.
        self.CONTINUOUS_HIGH_RES_MODE_2 = 0x11
        # Starte Messungen ab 1 Lux.
        # Nach messung wird Gerät in einen inaktiven Zustand gesetzt.
        self.ONE_TIME_HIGH_RES_MODE_1 = 0x20
        # Starte Messungen ab 0.5 Lux.
        # Nach messung wird Gerät in einen inaktiven Zustand gesetzt.
        self.ONE_TIME_HIGH_RES_MODE_2 = 0x21
        # Starte Messungen ab 4 Lux.
        # Nach messung wird Gerät in einen inaktiven Zustand gesetzt.
        self.ONE_TIME_LOW_RES_MODE = 0x23


    def convert_to_number(self, data):

        # Einfache Funktion um 2 Bytes Daten
        # in eine Dezimalzahl umzuwandeln
        return ((data[1] + (256 * data[0])) / 1.2)

    def read_light(self):

        data = self._bus.read_i2c_block_data(self.DEVICE,self.ONE_TIME_HIGH_RES_MODE_1)
        return self.convert_to_number(data)

class SimulatedLightSensor(LightSensor):
    BASE_LUX = 300.0

    def read_light(self):
        return round(self.BASE_LUX + random.uniform(-20.0, 20.0), 1)
    

def run_light_sensor(mqtt_client, sensor: LightSensor):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"light_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.log")

    while True:
        brightness = sensor.read_light()

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        log_entry = f"{datetime.datetime.now(datetime.timezone.utc)}, Brightness: {brightness} Lm\n"
        with open(log_file, "a") as f:
            f.write(log_entry)

        publish_message(
            client=mqtt_client, 
            sensor="Light",
            fields={"brightness": brightness},
            timestamp=timestamp
        )

        time.sleep(1)