from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    CURATOR = "curator"


class NotificationType(str, Enum):
    NEW_TASK = "new_task"
    NEW_INVITE = "new_invite"
    PROJECT_CLOSED = "project_closed"
    DEADLINE = "deadline"
    REMOVED_FROM_PROJECT = "removed_from_project"


class LevelEducation(str, Enum):
    SECONDARY_SPECIAL = "secondary_special"
    BACHELOR = "bachelor"
    SPECIALIST = "specialist"
    MASTER = "master"
    POSTGRADUATE = "postgraduate"
    DOCTORATE = "doctorate"


class TeamRole(str, Enum):
    TEAM_LEAD = "team_lead"
    BACKEND = "backend"
    FRONTEND = "frontend"
    DEVOPS = "devops"
    MANAGER = "manager"
    PRODUCT_MANAGER = "product_manager"
    BUSINESS_ANALYST = "business_analyst"
    CURATOR = "curator"


class UserStatus(str, Enum):
    OWNER = "owner"
    MEMBER = "member"
    INVATED = "invated"  # оставил как в схеме


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    TO_DO = "TO_DO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_TEST = "IN_TEST"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"


class InvitationStatus(str, Enum):
    POSTED = "posted"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class Faculty(str, Enum):
    RADIO_AND_TV = "radio_and_tv"
    INFORMATION_TECHNOLOGY = "information_technology"
    CYBERNETICS_AND_SECURITY = "cybernetics_and_security"
    NETWORKS_AND_COMMUNICATION = "networks_and_communication"
    DIGITAL_ECONOMY_AND_MEDIA = "digital_economy_and_media"
