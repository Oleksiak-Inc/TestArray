from pydantic import BaseModel, Field

class DeviceBase(BaseModel):
    name_external: str = Field(..., max_length=255)
    name_internal: str | None = Field(None, max_length=255)
    cpu: str | None = Field(None, max_length=255)
    gpu: str | None = Field(None, max_length=255)
    ram: int | None = None
    project_id: int

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name_external: str | None = Field(None, max_length=255)
    name_internal: str | None = Field(None, max_length=255)
    cpu: str | None = Field(None, max_length=255)
    gpu: str | None = Field(None, max_length=255)
    ram: int | None = None
    project_id: int | None = None

class DeviceOut(DeviceBase):
    id: int
    name_external: str
    name_internal: str | None
    cpu: str | None
    gpu: str | None
    ram: int | None

    class Config:
        from_attributes = True