# SPDX-FileCopyrightText: 2018-2023 Espressif Systems (Shanghai) CO LTD
# SPDX-License-Identifier: Apache-2.0
#

import bleak
import platform
import logging

logger = logging.getLogger('BLEWiFiProvisioner.transport')

# --------------------------------------------------------------------

def device_sort(device):
    return device[0].address


class BLE_Bleak_Client:
    def __init__(self, iface, verbose=None):
        self.adapter = None
        self.adapter_props = None
        self.characteristics = dict()
        self.device = None
        self.devname = None
        self.nu_lookup = None
        self.services = None
        self.srv_uuid_adv = None
        
        self.iface = iface
        self.verbose = verbose

    async def discover(self):
        return await bleak.BleakScanner.discover(return_adv=True, adapter=self.iface)
    
    async def connect(self, devname, devaddr):
        self.devname = devname
        self.devaddr = devaddr

        try:
            discovery = await bleak.BleakScanner.discover(return_adv=True, adapter=self.iface)
            devices = list(discovery.values())
        except bleak.exc.BleakDBusError as e:
            if str(e) == '[org.bluez.Error.NotReady] Resource Not Ready':
                raise RuntimeError('Bluetooth is not ready. Maybe try `bluetoothctl power on`?')
            raise

        found_device = None
        
        for d in devices:
            if d[0].name is not None and d[0].name == self.devname:
                found_device = d
            elif d[0].address == self.devaddr:
                found_device = d

        if not found_device:
            raise RuntimeError('Device not found')

        uuids = found_device[1].service_uuids
        # There should be 1 service UUID in advertising data
        # If bluez had cached an old version of the advertisement data
        # the list of uuids may be incorrect, in which case connection
        # or service discovery may fail the first time. If that happens
        # the cache will be refreshed before next retry
        if len(uuids) == 1:
            self.srv_uuid_adv = uuids[0]
        if self.verbose:
            logger.log(level=logging.INFO, msg='Connecting...')
        self.device = bleak.BleakClient(found_device[0].address, adapter=self.iface)
        await self.device.connect()
        # must be paired on Windows to access characteristics;
        # cannot be paired on Mac
        if platform.system() == 'Windows':
            await self.device.pair()

        if self.verbose:
            logger.log(level=logging.INFO, msg='Getting Services...')
        services = self.device.services

        service = services[self.srv_uuid_adv]
        if not service:
            await self.device.disconnect()
            self.device = None
            raise RuntimeError('Provisioning service not found')

        nu_lookup = dict()
        for characteristic in service.characteristics:
            for descriptor in characteristic.descriptors:
                if descriptor.uuid[4:8] != '2901':
                    continue
                readval = await self.device.read_gatt_descriptor(descriptor.handle)
                found_name = ''.join(chr(b) for b in readval).lower()
                nu_lookup[found_name] = characteristic.uuid
                self.characteristics[characteristic.uuid] = characteristic

        # Create lookup table
        self.nu_lookup = nu_lookup

        return True

    def get_nu_lookup(self):
        return self.nu_lookup

    def has_characteristic(self, uuid):
        logger.log(level=logging.INFO, msg='checking for characteristic ' + uuid)
        if uuid in self.characteristics:
            return True
        return False

    async def disconnect(self, verbose):
        if self.device:
            if verbose:
                logger.log(level=logging.INFO, msg='Disconnecting...')
            if platform.system() == 'Windows':
                await self.device.unpair()
            await self.device.disconnect()
            self.device = None
            self.nu_lookup = None
            self.characteristics = dict()

    async def send_data(self, characteristic_uuid, data):
        await self.device.write_gatt_char(characteristic_uuid, bytearray(data.encode('latin-1')), True)
        readval = await self.device.read_gatt_char(characteristic_uuid)
        return ''.join(chr(b) for b in readval)
