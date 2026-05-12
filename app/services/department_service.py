from fastapi import HTTPException, status

from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.department import (
    DepartmentCreate,
    DepartmentDetailResponse,
    DepartmentRead,
    DepartmentTreeRead,
    DepartmentUpdate,
)


class DepartmentService:
    def __init__(
        self,
        department_repository: DepartmentRepository,
        employee_repository: EmployeeRepository,
    ) -> None:
        self.department_repository = department_repository
        self.employee_repository = employee_repository

    def create_department(self, payload: DepartmentCreate) -> DepartmentRead:
        if payload.parent_id is not None:
            parent = self.department_repository.get_by_id(payload.parent_id)
            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent department not found",
                )

        existing_department = self.department_repository.get_by_parent_and_name(
            parent_id=payload.parent_id,
            name=payload.name,
        )
        if existing_department is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department with this name already exists in this parent",
            )

        department = Department(name=payload.name, parent_id=payload.parent_id)
        created_department = self.department_repository.create(department)
        return DepartmentRead.model_validate(created_department)

    def get_department_tree(
        self,
        department_id: int,
        depth: int,
        include_employees: bool,
    ) -> DepartmentDetailResponse:
        department = self.department_repository.get_by_id_with_relations(department_id)
        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )

        tree = self._build_department_tree(
            department=department,
            depth=depth,
            include_employees=include_employees,
        )
        return DepartmentDetailResponse(department=tree)

    def update_department(
        self,
        department_id: int,
        payload: DepartmentUpdate,
    ) -> DepartmentRead:
        department = self.department_repository.get_by_id(department_id)
        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )

        fields_set = payload.model_fields_set
        name_was_provided = "name" in fields_set
        parent_was_provided = "parent_id" in fields_set

        new_name = payload.name if name_was_provided else department.name
        new_parent_id = payload.parent_id if parent_was_provided else department.parent_id

        if parent_was_provided and new_parent_id is not None:
            self._ensure_no_cycle(
                department_id=department_id,
                new_parent_id=new_parent_id,
            )

        existing_department = self.department_repository.get_by_parent_and_name(
            parent_id=new_parent_id,
            name=new_name,
        )
        if existing_department is not None and existing_department.id != department_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department with this name already exists in this parent",
            )

        if name_was_provided:
            department.name = payload.name  # type: ignore[assignment]

        if parent_was_provided:
            department.parent_id = payload.parent_id

        updated_department = self.department_repository.update(department)
        return DepartmentRead.model_validate(updated_department)

    def delete_department(
        self,
        department_id: int,
        mode: str,
        reassign_to_department_id: int | None,
    ) -> None:
        department = self.department_repository.get_by_id(department_id)
        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )

        if mode == "cascade":
            self.department_repository.delete(department)
            return

        if mode == "reassign":
            self._delete_with_reassign(
                department=department,
                reassign_to_department_id=reassign_to_department_id,
            )
            return

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mode. Use cascade or reassign",
        )

    def _delete_with_reassign(
        self,
        department: Department,
        reassign_to_department_id: int | None,
    ) -> None:
        if reassign_to_department_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="reassign_to_department_id is required",
            )

        if reassign_to_department_id == department.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot reassign employees to deleted department",
            )

        target_department = self.department_repository.get_by_id(reassign_to_department_id)
        if target_department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reassign target department not found",
            )

        # In reassign mode we move employees only. To avoid ambiguous behavior,
        # deleting departments with children is forbidden and documented in README.
        if self.department_repository.has_children(department.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete department with children in reassign mode",
            )

        self.employee_repository.reassign_employees(
            from_department_id=department.id,
            to_department_id=reassign_to_department_id,
        )
        self.department_repository.delete(department)

    def _ensure_no_cycle(self, department_id: int, new_parent_id: int) -> None:
        if department_id == new_parent_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department cannot be parent of itself",
            )

        current_parent_id: int | None = new_parent_id
        while current_parent_id is not None:
            if current_parent_id == department_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot move department inside its own subtree",
                )

            parent = self.department_repository.get_by_id(current_parent_id)
            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent department not found",
                )

            current_parent_id = parent.parent_id

    def _build_department_tree(
        self,
        department: Department,
        depth: int,
        include_employees: bool,
    ) -> DepartmentTreeRead:
        employees = []
        if include_employees:
            employees = sorted(
                department.employees,
                key=lambda employee: employee.full_name,
            )

        children = []
        if depth > 0:
            children = [
                self._build_department_tree(
                    department=child,
                    depth=depth - 1,
                    include_employees=include_employees,
                )
                for child in sorted(department.children, key=lambda item: item.name)
            ]

        return DepartmentTreeRead(
            id=department.id,
            name=department.name,
            parent_id=department.parent_id,
            created_at=department.created_at,
            employees=employees,
            children=children,
        )
