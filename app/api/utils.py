import netifaces
from app.config import EDGE_GATEWAY_WLAN_IFACE, BLE_PROV_MAX_RETRIES

def get_wlan_iface_address():
    try:
        mac = netifaces.ifaddresses(EDGE_GATEWAY_WLAN_IFACE)[netifaces.AF_LINK][0]["addr"]
        return mac.upper()
    except (KeyError, IndexError):
        return None 

async def provision_ble_devices(devices, provisioner):
    _not_prov_devices = []
    _prov_devices = []
    for device in devices:
        await provisioner.connect(**device.model_dump())
        attempt = 0 # Counter
        _provisioned = False
        # Loop until the maximum number of retries is reached
        while attempt < BLE_PROV_MAX_RETRIES:
            try:
                # Attempt to provision the device
                await provisioner.prov_device()
                _prov_devices.append(device.device_name)
                _provisioned = True
                break  # Break the loop if provisioning is successful
            except:
                # Increment the counter and retry if an exception occurs
                attempt += 1

        # Check if the device was not provisioned after all retries
        if not _provisioned:
            _not_prov_devices.append(device.device_name)

        # Disconnect the provisioner after the provisioning attempts
        await provisioner.disconnect()
    return _not_prov_devices,_prov_devices