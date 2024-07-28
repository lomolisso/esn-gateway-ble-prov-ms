"""
This module contains the pydantic models (schemas) for the API.
08/10/2023
"""

from pydantic import BaseModel

class WlanIfaceAddress(BaseModel):
    device_address: str

class BLEDevice(BaseModel):
    device_name: str
    device_address: str

class BLEDeviceWithPoP(BLEDevice):
    device_pop: str
