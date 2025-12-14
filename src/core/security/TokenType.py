from enum import Enum


class TokenType(str, Enum):
    ADMIN_ACCESS = "admin_access"
    ADMIN_REFRESH = "admin_refresh"

    USER_ACCESS = "user_access"
    USER_REFRESH = "user_refresh"
