"""
SPDX-FileCopyrightText: 2018-2022 Espressif Systems (Shanghai) CO LTD
SPDX-License-Identifier: Apache-2.0
"""

import time
import logging

from . import prov
from . import security
from . import transport

TAG = "BLEWiFiProvisioner"

class BLEWiFiProvisioner:
    def __init__(self, wifi_ssid, wifi_passphrase, iface, verbose=False):
        self.ssid = wifi_ssid
        self.passphrase = wifi_passphrase
        self.iface = iface
        self.verbose = verbose

        self._init_logger()
        self._init_transport(iface=self.iface)

    # --- main API ---
    async def discover(self, service_name_prefix="", fallback_oui=""):
        devices = await self._tp.discover()
        filtered_devices = []
        for dev_addr, (_, adv_data) in devices.items():
            if adv_data.local_name is not None:
                if adv_data.local_name.startswith(service_name_prefix):
                    filtered_devices.append({
                        "device_name": adv_data.local_name,
                        "device_address": dev_addr,
                    })
            else: # fallback to OUI
                if dev_addr.startswith(fallback_oui):
                    nic_bytes = "".join(dev_addr.split(":")[3:])
                    filtered_devices.append({
                        "device_name": f"ESP32_{nic_bytes}",
                        "device_address": dev_addr,
                    })
        return filtered_devices
    
    async def connect(self, device_name, device_address, device_pop):
        self._init_security(pop=device_pop)
        try:
            await self._tp.connect(devname=device_name, devaddr=device_address)
        except RuntimeError as e:
            raise RuntimeError(e)

        self.log("==== Starting Session ====")
        if not await self._establish_session():
            self.log(
                "Failed to establish session. Ensure that security scheme and proof of possession are correct"
            )
            raise RuntimeError("Error in establishing session")
        self.log("==== Session Established ====")

    async def get_version(self):
        response = None
        try:
            response = await self._tp.send_data("proto-ver", "---")
        except RuntimeError as e:
            raise RuntimeError(e)
        return response

    async def custom_data(self, custom_data):
        try:
            message = prov.custom_data_request(self._sec, custom_data)
            response = await self._tp.send_data("custom-data", message)
            return prov.custom_data_response(self._sec, response) == 0
        except RuntimeError as e:
            raise RuntimeError(e)

    async def scan_wifi_APs(self, tp, sec):
        """
        Read at most 4 entries at a time. This is because if we are using BLE transport
        then the response packet size should not exceed the present limit of 256 bytes of
        characteristic value imposed by protocomm_ble. This limit may be removed in the
        future
        """

        APs = []
        group_channels = 0
        readlen = 100
        readlen = 4

        try:
            message = prov.scan_start_request(
                sec, blocking=True, group_channels=group_channels
            )
            start_time = time.time()
            response = await tp.send_data("prov-scan", message)
            stop_time = time.time()
            self.log(
                "++++ Scan process executed in " + str(stop_time - start_time) + " sec"
            )
            prov.scan_start_response(sec, response)

            message = prov.scan_status_request(sec)
            response = await tp.send_data("prov-scan", message)
            result = prov.scan_status_response(sec, response)
            self.log("++++ Scan results : " + str(result["count"]))
            if result["count"] != 0:
                index = 0
                remaining = result["count"]
                while remaining:
                    count = [remaining, readlen][remaining > readlen]
                    message = prov.scan_result_request(sec, index, count)
                    response = await tp.send_data("prov-scan", message)
                    APs += prov.scan_result_response(sec, response)
                    remaining -= count
                    index += count
        except RuntimeError as e:
            raise RuntimeError(e)

    async def reset_wifi(self):
        try:
            message = prov.ctrl_reset_request(self._sec)
            response = await self._tp.send_data("prov-ctrl", message)
            prov.ctrl_reset_response(self._sec, response)

        except RuntimeError as e:
            raise RuntimeError(e)

    async def reprov_wifi(self, tp, sec):
        try:
            message = prov.ctrl_reprov_request(sec)
            response = await tp.send_data("prov-ctrl", message)
            prov.ctrl_reprov_response(sec, response)

        except RuntimeError as e:
            raise RuntimeError(e)

    async def prov_device(self):
        self.log("==== Sending Wi-Fi Credentials to Target ====")
        if not await self._send_wifi_config():
            raise RuntimeError("Error in send Wi-Fi config")
        self.log("==== Wi-Fi Credentials sent successfully ====")

        self.log("==== Applying Wi-Fi Config to Target ====")
        if not await self._apply_wifi_config():
            raise RuntimeError("Error in apply Wi-Fi config")
        self.log("==== Apply config sent successfully ====")

        await self._wait_wifi_connected()

    async def disconnect(self):
        await self._tp.disconnect()

    def log(self, msg):
        if self.verbose and self._logger:
            self._logger.info(msg=msg)

    # --- private methods ---

    def _init_logger(self):
        TAG = "BLEWiFiProvisioner"
        self._logger = logging.getLogger(TAG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(f"[{TAG}] "+"%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def _init_security(self, pop):
        self._sec = security.Security1(pop, self.verbose)

    def _init_transport(self, iface="hci0"):
        self._tp = transport.Transport_BLE(iface=iface, verbose=self.verbose)

    async def _establish_session(self):
        try:
            response = None
            while True:
                request = self._sec.security_session(response)
                if request is None:
                    break
                response = await self._tp.send_data("prov-session", request)
                if response is None:
                    return False
            return True
        except RuntimeError as e:
            raise RuntimeError(e)

    async def _send_wifi_config(self):
        try:
            message = prov.config_set_config_request(
                self._sec, self.ssid, self.passphrase
            )
            response = await self._tp.send_data("prov-config", message)
            return prov.config_set_config_response(self._sec, response) == 0
        except RuntimeError as e:
            raise RuntimeError(e)

    async def _apply_wifi_config(self):
        try:
            message = prov.config_apply_config_request(self._sec)
            response = await self._tp.send_data("prov-config", message)
            return prov.config_apply_config_response(self._sec, response) == 0
        except RuntimeError as e:
            raise RuntimeError(e)

    async def _get_wifi_config(self):
        try:
            message = prov.config_get_status_request(self._sec)
            response = await self._tp.send_data("prov-config", message)
            return prov.config_get_status_response(self._sec, response, verbose=self.verbose)
        except RuntimeError as e:
            raise RuntimeError(e)

    async def _wait_wifi_connected(self):
        """
        Wait for provisioning to report Wi-Fi is connected

        Returns True if Wi-Fi connection succeeded, False if connection consistently failed
        """
        TIME_PER_POLL = 5
        retry = 3

        while True:
            time.sleep(TIME_PER_POLL)
            ret = await self._get_wifi_config()
            self.log(f"==== Wi-Fi connection state: {ret}  ====")
            if ret == "connecting":
                continue
            elif ret == "connected":
                self.log("==== Provisioning was successful ====")
                return True
            elif retry > 0:
                retry -= 1
                self.log(
                    "Waiting to poll status again (status %s, %d tries left)..."
                    % (ret, retry)
                )
            else:
                self.log("---- Provisioning failed! ----")
                return False
