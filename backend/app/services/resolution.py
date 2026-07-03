from db.models.resolutions import Resolutions
from .utils.service import BaseService


class ResolutionService(BaseService):
    def get_resolution(self, resolution_id: int):
        return self.get_by_id(Resolutions, resolution_id)

    def get_resolution_by_hw(self, h: int, w: int):
        return self.db.query(Resolutions).filter(
            Resolutions.h == h, Resolutions.w == w
        ).first()

    def list_resolutions(self):
        return self.db.query(Resolutions).all()

    def create_resolution(self, resolution_data: dict):
        return self.create(Resolutions, resolution_data)

    def update_resolution(self, resolution_id: int, resolution_data: dict):
        resolution = self.get_resolution(resolution_id)
        if not resolution:
            return None
        return self.update(resolution, resolution_data)

    def delete_resolution(self, resolution_id: int):
        resolution = self.get_resolution(resolution_id)
        if not resolution:
            return None
        return self.delete(resolution)