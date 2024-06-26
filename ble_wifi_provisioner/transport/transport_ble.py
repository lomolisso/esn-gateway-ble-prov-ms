# SPDX-FileCopyrightText: 2018-2023 Espressif Systems (Shanghai) CO LTD
# SPDX-License-Identifier: Apache-2.0
#

from .ble_cli import BLE_Bleak_Client
from .transport import Transport


class Transport_BLE(Transport):
    def __init__(self, iface, verbose):
        self.name_uuid_lookup = None
        self.verbose = verbose

        # Get BLE client module
        self.cli = BLE_Bleak_Client(iface=iface, verbose=verbose)

    async def discover(self):
        return await self.cli.discover()

    async def connect(self, devname, devaddr):
        # Use client to connect to BLE device and bind to service
        if not await self.cli.connect(devname=devname, devaddr=devaddr):
            raise RuntimeError("Failed to initialize transport")

        self.name_uuid_lookup = self.cli.get_nu_lookup()

    async def disconnect(self):
        await self.cli.disconnect(verbose=self.verbose)

    async def send_data(self, ep_name, data):
        # Write (and read) data to characteristic corresponding to the endpoint
        if ep_name not in self.name_uuid_lookup.keys():
            raise RuntimeError(f"Invalid endpoint: {ep_name}")
        return await self.cli.send_data(self.name_uuid_lookup[ep_name], data)
