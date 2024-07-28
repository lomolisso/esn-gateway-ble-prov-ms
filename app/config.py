import os
from dotenv import load_dotenv

# Retrieve enviroment variables from .env file
load_dotenv()

SECRET_KEY: str = os.environ.get("SECRET_KEY")
ESN_GATEWAY_API_URL = os.environ.get("ESN_GATEWAY_API_URL")

EDGE_GATEWAY_BLE_IFACE = os.getenv("EDGE_GATEWAY_BLE_IFACE", "hci0")
EDGE_GATEWAY_WIFI_SSID = os.getenv("EDGE_GATEWAY_WIFI_SSID")
EDGE_GATEWAY_WIFI_PASSPHRASE = os.getenv("EDGE_GATEWAY_WIFI_PASSPHRASE")

EDGE_SENSOR_SERVICE_NAME_PREFIX = os.getenv("EDGE_SENSOR_SERVICE_NAME_PREFIX", "ESP32_")
EDGE_SENSOR_OUI = os.getenv("EDGE_SENSOR_OUI", "B0:A7:32")

BLE_PROV_MAX_RETRIES = int(os.getenv("BLE_PROV_MAX_RETRIES", 3))

# CORS
ORIGINS: list = [
    "*"
]