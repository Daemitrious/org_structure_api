from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class Department(Base):
    __tablename__ = "departments"

    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "name",
            name="uq_departments_parent_id_name",
        ),
        Index(
            "uq_departments_root_name",
            "name",
            unique=True,
            postgresql_where=text("parent_id IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    parent: Mapped["Department | None"] = relationship(
        "Department",
        remote_side="Department.id",
        back_populates="children",
    )

    children: Mapped[list["Department"]] = relationship(
        "Department",
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
