from fastapi import HTTPException, status

from app.models.employee import Employee
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeRead


class EmployeeService:
    def __init__(
        self,
        employee_repository: EmployeeRepository,
        department_repository: DepartmentRepository,
    ) -> None:
        self.employee_repository = employee_repository
        self.department_repository = department_repository

    def create_employee(
        self,
        department_id: int,
        payload: EmployeeCreate,
    ) -> EmployeeRead:
        department = self.department_repository.get_by_id(department_id)
        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )

        employee = Employee(
            department_id=department_id,
            full_name=payload.full_name,
            position=payload.position,
            hired_at=payload.hired_at,
        )
        created_employee = self.employee_repository.create(employee)
        return EmployeeRead.model_validate(created_employee)
