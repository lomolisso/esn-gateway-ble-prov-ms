from app.api import schemas
from app.dependencies import get_ble_provisioner
from fastapi import APIRouter, Depends
from app.api import utils as api_utils
from app.config import (
    EDGE_SENSOR_SERVICE_NAME_PREFIX,
    EDGE_SENSOR_OUI,
)
from typing import List

ble_router = APIRouter(prefix="/api/v1")

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


@ble_router.post("/provision")
async def provision_device(
    devices: list[schemas.BLEDeviceWithPoP], provisioner=Depends(get_ble_provisioner)
) -> list[schemas.BLEDevice]:
    _, prov_devices = await api_utils.provision_ble_devices(
        devices, provisioner
    )

    return [
        schemas.BLEDevice(**d.model_dump())
        for d in prov_devices
    ]
