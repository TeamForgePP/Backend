import bcrypt

from src.core.db.models import Users
from src.modules.admin.schemas import UserRead


def hash_password(raw_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(raw_password.encode("utf-8"), hashed_password.encode("utf-8"))


def user_to_read_model(user: Users) -> UserRead:
    return UserRead.model_validate(user)
