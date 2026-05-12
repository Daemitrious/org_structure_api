from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_department_service, get_employee_service
from app.schemas.department import (
    DepartmentCreate,
    DepartmentDetailResponse,
    DepartmentRead,
    DepartmentUpdate,
)
from app.schemas.employee import EmployeeCreate, EmployeeRead
from app.services.department_service import DepartmentService
from app.services.employee_service import EmployeeService

router = APIRouter(tags=["departments"])

#krushinski dima
@router.post(
    "/departments/",
    response_model=DepartmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    payload: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentRead:
    return service.create_department(payload)


@router.post(
    "/departments/{department_id}/employees/",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    department_id: int,
    payload: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeRead:
    return service.create_employee(department_id=department_id, payload=payload)


@router.get(
    "/departments/{department_id}",
    response_model=DepartmentDetailResponse,
)
def get_department(
    department_id: int,
    depth: int = Query(default=1, ge=0, le=5),
    include_employees: bool = Query(default=True),
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentDetailResponse:
    return service.get_department_tree(
        department_id=department_id,
        depth=depth,
        include_employees=include_employees,
    )


@router.patch(
    "/departments/{department_id}",
    response_model=DepartmentRead,
)
def update_department(
    department_id: int,
    payload: DepartmentUpdate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentRead:
    return service.update_department(department_id=department_id, payload=payload)


@router.delete(
    "/departments/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    department_id: int,
    mode: Literal["cascade", "reassign"] = Query(default="cascade"),
    reassign_to_department_id: int | None = Query(default=None),
    service: DepartmentService = Depends(get_department_service),
) -> None:
    service.delete_department(
        department_id=department_id,
        mode=mode,
        reassign_to_department_id=reassign_to_department_id,
    )
