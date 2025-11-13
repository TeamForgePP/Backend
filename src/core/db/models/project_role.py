from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum as Enumm
from src.core.db.base import Base

class TeamRole(Enumm):
    TeamLead = "team_lead"
    Backend = "backend"
    Frontend = "frontend"
    Devops = "devops"
    Manager = "manager"
    ProductManager = "product_manager"
    BusinessAnalyst = "business_analyst"
    Curator = "Curator"

class ProjectRole(Base):
    #project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    #user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role: Mapped[TeamRole] = mapped_column(Enum(TeamRole), nullable=False)
