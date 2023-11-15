from app.config import EDGE_GATEWAY_WIFI_SSID, EDGE_GATEWAY_WIFI_PASSPHRASE, EDGE_GATEWAY_BLE_IFACE
from app.ble_wifi_provisioner import BLEWiFiProvisioner


def get_ble_provisioner():
    provisioner = BLEWiFiProvisioner(
        wifi_ssid=EDGE_GATEWAY_WIFI_SSID,
        wifi_passphrase=EDGE_GATEWAY_WIFI_PASSPHRASE,
        iface=EDGE_GATEWAY_BLE_IFACE
    )
    yield provisioner