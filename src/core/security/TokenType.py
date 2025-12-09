from enum import Enum


class TokenType(str, Enum):
    ADMIN_ACCESS = "admin_access"
    ADMIN_REFRESH = "admin_refresh"
