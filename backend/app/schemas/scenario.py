from pydantic import BaseModel, Field, ConfigDict


class ScenarioBase(BaseModel):
    name: str = Field(..., max_length=255)


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)


class ScenarioOut(ScenarioBase):
    id: int

    model_config = ConfigDict(from_attributes=True)