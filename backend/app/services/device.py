from sqlalchemy.orm import Session, joinedload
from db.models.devices import Devices
from db.models.projects import Projects
from .utils.service import BaseService


class DeviceService(BaseService):
    def get_device(self, device_id: int):
        return self.db.query(Devices).filter(Devices.id == device_id).first()

    def get_device_with_project(self, device_id: int):
        return self.db.query(Devices).filter(Devices.id == device_id).options(
            joinedload(Devices.project)
        ).first()

    def list_devices_by_project(self, project_id: int):
        return self.db.query(Devices).filter(Devices.project_id == project_id).all()

    def create_device(self, device_data):
        device = Devices(**device_data)
        self.db.add(device)
        self.commit_and_refresh(device)
        return device

    def update_device(self, device_id: int, device_data):
        device = self.get_device(device_id)
        if not device:
            return None
        for key, value in device_data.items():
            setattr(device, key, value)
        self.commit_and_refresh(device)
        return device

    def delete_device(self, device_id: int):
        device = self.get_device(device_id)
        if not device:
            return None
        self.db.delete(device)
        self.db.commit()
        return device
