from enum import Enum


class TaskPriority(Enum):
    High = "high"
    Medium = "medium"
    Low = "Low"


class TaskStatus(Enum):
    ToDo = "TO_DO"
    InProgress = "IN_PROGRESS"
    InTest = "IN_TEST"
    InReview = "IN_REVIEW"
    Done = "DONE"


class TeamRole(Enum):
    TeamLead = "team_lead"
    Backend = "backend"
    Frontend = "frontend"
    Devops = "devops"
    Manager = "manager"
    ProductManager = "product_manager"
    BusinessAnalyst = "business_analyst"
    Curator = "Curator"


class UserStatus(Enum):
    Owner = "owner"
    Member = "member"
    Invited = "invited"


class InvitationStatus(Enum):
    Posted = "posted"
    Rejected = "rejected"
    Accepted = "accepted"


class NotificationType(Enum):
    NewTask = "new_task"
    NewInvite = "new_invite"
    ProjectClosed = "project_closed"
    Deadline = "deadline"
    RemoverFromProject = "removed_from_project"
