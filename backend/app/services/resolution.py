from db.models.resolutions import Resolutions
from .utils.service import BaseService


class ResolutionService(BaseService):
    def get_resolution(self, resolution_id: int):
        return self.db.query(Resolutions).filter(Resolutions.id == resolution_id).first()

    def get_resolution_by_hw(self, h: int, w: int):
        return self.db.query(Resolutions).filter(
            Resolutions.h == h, Resolutions.w == w
        ).first()

    def list_resolutions(self):
        return self.db.query(Resolutions).all()

    def create_resolution(self, resolution_data: dict):
        resolution = Resolutions(**resolution_data)
        self.db.add(resolution)
        self.commit_and_refresh(resolution)
        return resolution

    def update_resolution(self, resolution_id: int, resolution_data: dict):
        resolution = self.get_resolution(resolution_id)
        if not resolution:
            return None
        for key, value in resolution_data.items():
            setattr(resolution, key, value)
        self.commit_and_refresh(resolution)
        return resolution

    def delete_resolution(self, resolution_id: int):
        resolution = self.get_resolution(resolution_id)
        if not resolution:
            return None
        self.db.delete(resolution)
        self.db.commit()
        return resolution