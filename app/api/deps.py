from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.services.department_service import DepartmentService
from app.services.employee_service import EmployeeService


def get_db() -> Generator[Session, None, None]:
    yield from get_db_session()


def get_department_service(db: Session = Depends(get_db)) -> DepartmentService:
    department_repository = DepartmentRepository(db)
    employee_repository = EmployeeRepository(db)
    return DepartmentService(
        department_repository=department_repository,
        employee_repository=employee_repository,
    )


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    department_repository = DepartmentRepository(db)
    employee_repository = EmployeeRepository(db)
    return EmployeeService(
        employee_repository=employee_repository,
        department_repository=department_repository,
    )
