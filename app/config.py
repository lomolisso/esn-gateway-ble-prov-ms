import os
from dotenv import load_dotenv

# Retrieve enviroment variables from .env file
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
BLE_PROV_MICROSERVICE_HOST = os.environ.get("BLE_PROV_MICROSERVICE_HOST", "host.docker.internal")
BLE_PROV_MICROSERVICE_PORT = os.environ.get("BLE_PROV_MICROSERVICE_PORT", "8006")
EDGE_GATEWAY_BLE_IFACE = os.environ.get("EDGE_GATEWAY_BLE_IFACE", "hci0")
EDGE_GATEWAY_WIFI_SSID = os.environ.get("EDGE_GATEWAY_WIFI_SSID", "raspberry_wifi")
EDGE_GATEWAY_WIFI_PASSPHRASE = os.environ.get("EDGE_GATEWAY_WIFI_PASSPHRASE", "raspberry_wifi")
EDGE_SENSOR_SERVICE_NAME_PREFIX = os.environ.get("EDGE_SENSOR_SERVICE_NAME_PREFIX", "ESP32_")
EDGE_SENSOR_OUI = os.environ.get("EDGE_SENSOR_OUI", "B0:A7:32")
BLE_PROV_MAX_RETRIES = int(os.environ.get("BLE_PROV_MAX_RETRIES", "3"))

# CORS
ORIGINS: list = [
    "*"
]