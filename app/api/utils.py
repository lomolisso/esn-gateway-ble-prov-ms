from app.config import BLE_PROV_MAX_RETRIES

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
                _prov_devices.append(device)
                _provisioned = True
                break  # Break the loop if provisioning is successful
            except:
                # Increment the counter and retry if an exception occurs
                attempt += 1

        # Check if the device was not provisioned after all retries
        if not _provisioned:
            _not_prov_devices.append(device)

        # Disconnect the provisioner after the provisioning attempts
        await provisioner.disconnect()
    return _not_prov_devices,_prov_devices