from app.api import schemas
from app.dependencies import get_ble_provisioner
from fastapi import APIRouter, Depends
from app.api import utils as api_utils
from app.config import (
    EDGE_SENSOR_SERVICE_NAME_PREFIX,
    EDGE_SENSOR_OUI,
)
from typing import List

ble_router = APIRouter(prefix="/ble-prov-api")


@ble_router.get("/get-wlan-iface-address")
async def get_wlan_iface_address() -> schemas.WlanIfaceAddress:
    device_address = api_utils.get_wlan_iface_address()
    return schemas.WlanIfaceAddress(device_address=device_address)


@ble_router.get("/discover")
async def discover_devices(
    provisioner=Depends(get_ble_provisioner),
) -> List[schemas.BLEDevice]:
    return [
        schemas.BLEDevice(**d)
        for d in await provisioner.discover(
            service_name_prefix=EDGE_SENSOR_SERVICE_NAME_PREFIX,
            fallback_oui=EDGE_SENSOR_OUI,
        )
    ]


@ble_router.post("/prov-device")
async def provision_device(
    devices: list[schemas.BLEDeviceWithPoP], provisioner=Depends(get_ble_provisioner)
) -> schemas.BLEProvResponse:
    not_prov_devices, prov_devices = await api_utils.provision_ble_devices(
        devices, provisioner
    )

    return schemas.BLEProvResponse(
        provisioned=prov_devices, not_provisioned=not_prov_devices
    )
