from __future__ import annotations

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class ProjectReport(Base):
    # связь М2М между projects и reports
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    report_id: Mapped[UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("project_id", "report_id", name="pk_project_reports"),)

    project: Mapped["Project"] = relationship(back_populates="project_reports")
    report: Mapped["Report"] = relationship(back_populates="project_links")
