from sqlalchemy.orm import Session, joinedload
from db.models.devices import Devices
from db.models.projects import Projects
from .utils.service import BaseService


def _normalize_ram(value):
    if value is None:
        return None
    return str(value) if not isinstance(value, str) else value


class DeviceService(BaseService):
    def get_device(self, device_id: int):
        return self.get_by_id(Devices, device_id)

    def get_device_with_project(self, device_id: int):
        return self.db.query(Devices).filter(Devices.id == device_id).options(
            joinedload(Devices.project)
        ).first()

    def list_devices_by_project(self, project_id: int):
        return self.db.query(Devices).filter(Devices.project_id == project_id).all()

    def create_device(self, device_data):
        if device_data.get("ram") is not None:
            device_data = dict(device_data)
            device_data["ram"] = _normalize_ram(device_data["ram"])
        return self.create(Devices, device_data)

    def update_device(self, device_id: int, device_data):
        device = self.get_device(device_id)
        if not device:
            return None
        if device_data.get("ram") is not None:
            device_data = dict(device_data)
            device_data["ram"] = _normalize_ram(device_data["ram"])
        return self.update(device, device_data)

    def delete_device(self, device_id: int):
        device = self.get_device(device_id)
        if not device:
            return None
        return self.delete(device)
