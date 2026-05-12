from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.employee import EmployeeRead


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Department name cannot be empty")
        return value


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    parent_id: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Department name cannot be empty")
        return value


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None
    created_at: datetime


class DepartmentTreeRead(DepartmentRead):
    employees: list[EmployeeRead] = Field(default_factory=list)
    children: list[DepartmentTreeRead] = Field(default_factory=list)


class DepartmentDetailResponse(BaseModel):
    department: DepartmentTreeRead


DepartmentTreeRead.model_rebuild()
