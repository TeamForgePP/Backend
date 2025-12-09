from enum import Enum


class Faculty(str, Enum):
    CYBERNETICS_AND_SECURITY = "cybernetics_and_security"
    DIGITAL_ECONOMY_AND_MEDIA = "digital_economy_and_media"
    INFORMATION_TECHNOLOGY = "information_technology"
    NETWORKS_AND_COMMUNICATION = "networks_and_communication"
    RADIO_AND_TV = "radio_and_tv"


class InvitationStatus(Enum):
    Accepted = "accepted"
    Posted = "posted"
    Rejected = "rejected"


class LevelEducation(str, Enum):
    BACHELOR = "bachelor"
    DOCTORATE = "doctorate"
    MASTER = "master"
    POSTGRADUATE = "postgraduate"
    SECONDARY_SPECIAL = "secondary_special"
    SPECIALIST = "specialist"


class NotificationType(Enum):
    Deadline = "deadline"
    NewInvite = "new_invite"
    NewTask = "new_task"
    ProjectClosed = "project_closed"
    RemoverFromProject = "removed_from_project"


class TaskPriority(Enum):
    High = "high"
    Low = "Low"
    Medium = "medium"


class TaskStatus(Enum):
    Done = "DONE"
    InProgress = "IN_PROGRESS"
    InReview = "IN_REVIEW"
    InTest = "IN_TEST"
    ToDo = "TO_DO"


class TeamRole(Enum):
    Backend = "backend"
    BusinessAnalyst = "business_analyst"
    Curator = "Curator"
    Devops = "devops"
    Frontend = "frontend"
    Manager = "manager"
    ProductManager = "product_manager"
    TeamLead = "team_lead"


class UserRole(str, Enum):
    CURATOR = "curator"
    STUDENT = "student"


class UserStatus(Enum):
    Invited = "invited"
    Member = "member"
    Owner = "owner"


class SprintStatus(str, Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
