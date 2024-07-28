# ble_wifi_provisioner

`ble_wifi_provisioner` is a Python module designed to simplify WiFi credential provisioning for ESP32s via BLE. This module extends the functionality provided by [Espressif's esp_prov tool](https://github.com/espressif/esp-idf/tree/master/tools/esp_prov), which is an integral part of the ESP-IDF framework and is licensed under the Apache 2.0 license.

## Features:

- Uses the X25519 key exchange combined with proof of possession (PoP).
- Employs AES-CTR for encrypting and decrypting messages.
- Provides methods to connect, retrieve version, handle custom data, scan WiFi access points, reset WiFi settings, and provision devices.

## Licensing:

This project integrates features from the `esp_prov` tool developed by Espressif Systems, which is licensed under the Apache 2.0 license. The Apache 2.0 license is a permissive open-source license, allowing developers to freely use, modify, and distribute the software, provided the original copyright notice and disclaimer are preserved.

Given your changes, the **Usage** section should be updated as follows:

## Usage:

To utilize the `BLEWiFiProvisioner` class, follow the steps below:

1. **Initialization**:

   Begin by initializing the `BLEWiFiProvisioner` with the required parameters:

   ```python
   from ble_wifi_provisioner import BLEWiFiProvisioner

   pop = "Your_PoP"
   ssid = "Your_WiFi_SSID"
   passphrase = "Your_WiFi_Password"
   iface = "your_bluetooth_iface"

   provisioner = BLEWiFiProvisioner(pop, ssid, passphrase, iface=iface, verbose=True)
   ```

2. **Discover BLE Devices**:

   To discover BLE devices around:

   ```python
   discovered_devices = await provisioner.discover(
      service_name_prefix="ESP32_",
      fallback_oui="B0:A7:32"
   )
   for d in discovered_devices:
      service_name, service_address = d["device_name"], d["device_address"]
   ```
   Note that `fallback_oui` allows for finding devices by address if the service `local_name` is not available.

3. **Establishing a Connection**:

   Connect to the BLE device by passing the `device_name` and `device_address`:

   ```python
   device_name = "Your_Service_Name"
   device_address = "Your_Device_Address"
   await provisioner.connect(device_name, device_address)
   ```

4. **Interact with a Device**:

- **Get Protcomm Version**
  To get the version of the provisioner:

  ```python
  version = await provisioner.get_version()
  print(f"Provisioner Version: {version}")
  ```

- **Scan WiFi Access Points**:

  To scan for available WiFi access points:

  ```python
  access_points = await provisioner.scan_wifi_APs()
  for ap in access_points:
      print(ap)
  ```

- **Reset WiFi Settings**:

  If you need to reset the WiFi configurations on the device:

  ```python
  await provisioner.reset_wifi()
  ```

- **Sending Custom Data**:

  To send custom data to the device:

  ```python
  custom_data_to_send = "Your_Custom_Data_Here"
  success = await provisioner.custom_data(custom_data_to_send)
  if success:
      print("Custom data sent successfully!")
  else:
      print("Failed to send custom data.")
  ```

5. **Provision WiFi**:

   To provision the device with WiFi credentials:

   ```python
   await provisioner.prov_device()
   ```

6. **Disconnecting**:

   After you're done with provisioning, ensure to gracefully disconnect:

   ```python
   await provisioner.disconnect()
   ```

   Please note that any interaction with a BLEDevice should be wrapped in a `try/except` block as Exceptions might be raised. 
