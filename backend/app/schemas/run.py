from pydantic import BaseModel, Field

class RunBase(BaseModel):
    name: str = Field(..., max_length=255)