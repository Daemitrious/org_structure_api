from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self.session.get(Employee, employee_id)

    def create(self, employee: Employee) -> Employee:
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        return employee

    def reassign_employees(
        self,
        from_department_id: int,
        to_department_id: int,
    ) -> None:
        statement = (
            update(Employee)
            .where(Employee.department_id == from_department_id)
            .values(department_id=to_department_id)
        )
        self.session.execute(statement)
        self.session.commit()
