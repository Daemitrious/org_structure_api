from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.department import Department


class DepartmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, department_id: int) -> Department | None:
        return self.session.get(Department, department_id)

    def get_by_id_with_relations(self, department_id: int) -> Department | None:
        statement = (
            select(Department)
            .where(Department.id == department_id)
            .options(
                selectinload(Department.employees),
                selectinload(Department.children),
            )
        )
        return self.session.scalar(statement)

    def get_by_parent_and_name(
        self,
        parent_id: int | None,
        name: str,
    ) -> Department | None:
        statement = select(Department).where(
            Department.parent_id == parent_id,
            Department.name == name,
        )
        return self.session.scalar(statement)

    def create(self, department: Department) -> Department:
        self.session.add(department)
        self.session.commit()
        self.session.refresh(department)
        return department

    def update(self, department: Department) -> Department:
        self.session.commit()
        self.session.refresh(department)
        return department

    def delete(self, department: Department) -> None:
        self.session.delete(department)
        self.session.commit()

    def has_children(self, department_id: int) -> bool:
        statement = select(Department.id).where(Department.parent_id == department_id)
        return self.session.scalar(statement) is not None
