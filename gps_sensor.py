# from tinkerforge.ip_connection import IPConnection
# from tinkerforge.bricklet_gps_v3 import BrickletGPSV3
import datetime
import os
import time
import random
from abc import ABC, abstractmethod
from utils import publish_message

UID = "21Ld"  
HOST = "localhost"
GPS_PORT = 4223

class GPSSensor(ABC):
    @abstractmethod
    def get_coordinates(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

    def disconnect(self):
        pass

class TinkerforgeGPSSensor(GPSSensor):
    def __init__(self, uid=UID, host=HOST, port=GPS_PORT):
        from tinkerforge.ip_connection import IPConnection
        from tinkerforge.bricklet_gps_v3 import BrickletGPSV3
        self._ipcon = IPConnection()
        self._gps = BrickletGPSV3(uid, self._ipcon)
        self._ipcon.connect(host, port)
        time.sleep(0.2)

    def get_coordinates(self):
        return self._gps.get_coordinates()

    def get_status(self):
        return self._gps.get_status()
    
    def disconnect(self):
        self._ipcon.disconnect()

class CoordinatesData:
    """Mimics the named tuple returned by the real bricklet."""
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        
class SimulatedGPSSensor(GPSSensor):
    BASE_LAT = 52.5200
    BASE_LON = 13.4050

    def get_coordinates(self):
        """Returns (lat, lat_dir, lon, lon_dir)."""
        lat = self.BASE_LAT + random.uniform(-0.001, 0.001)
        lon = self.BASE_LON + random.uniform(-0.001, 0.001)
        # Tinkerforge uses NMEA-style format and returns microdegrees and
        # N/S, E/W indicators
        return CoordinatesData(
            latitude=int(lat * 1_000_000),
            longitude=int(lon * 1_000_000)
        )
    def get_status(self):
        """Returns (has_fix, satellites_used)."""
        return True, random.randint(4, 8)
    

def get_location(sensor: GPSSensor):
    
    try:
        fix, satellites_used = sensor.get_status()
        print(f"Fix level: {fix}, Satellites used: {satellites_used}")
    except Exception as e:
        print(f"Error getting GPS status: {e}")
        return None, None

    if isinstance(fix, bool):
        fix_level = 3 if fix else 1 
    else:
        fix_level = int(fix)

    if fix_level < 2:
        print("No valid fix (waiting for 2D or 3D fix).")
        sensor.disconnect()
        return None, None

    data = sensor.get_coordinates()
    lat = data.latitude / 1000000.0
    lon = data.longitude / 1000000.0

    if lat < 1.0 or lon < 1.0:
        print("Coordinates invalid.")
        return None, None

    print(f"Valid coordinates: {lat}, {lon}")
    return lat, lon

def run_gps(mqtt_client, sensor: GPSSensor):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"gps_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.log")

    while True:
        lat, lon = get_location(sensor)
        if lat is not None and lon is not None:
            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            log_entry = f"{datetime.datetime.now(datetime.timezone.utc)}, Latitude: {lat}, Longitude: {lon}\n"
            with open(log_file, "a") as f:
                f.write(log_entry)
            publish_message(
                client=mqtt_client,
                sensor="GPS",
                fields={"latitude": lat, "longitude": lon},
                timestamp=timestamp
            )
        time.sleep(1) 