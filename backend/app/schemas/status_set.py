from pydantic import BaseModel, Field, ConfigDict


class StatusSetBase(BaseModel):
    name: str = Field(..., max_length=255)


class StatusSetCreate(StatusSetBase):
    pass


class StatusSetUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)


class StatusSetOut(StatusSetBase):
    id: int

    model_config = ConfigDict(from_attributes=True)