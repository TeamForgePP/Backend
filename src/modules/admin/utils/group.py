from src.core.db.models import Groups
from src.modules.admin.schemas import GroupRead


def group_to_read_model(group: Groups) -> GroupRead:
    return GroupRead.model_validate(group)
