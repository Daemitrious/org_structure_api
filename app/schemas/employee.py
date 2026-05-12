from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmployeeCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    hired_at: date | None = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Employee full_name cannot be empty")
        return value

    @field_validator("position")
    @classmethod
    def validate_position(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Employee position cannot be empty")
        return value


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: date | None
    created_at: datetime
