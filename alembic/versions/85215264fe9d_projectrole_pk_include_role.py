"""projectrole pk include role

Revision ID: 85215264fe9d
Revises: 7cf4b9133b17
Create Date: 2026-01-20 10:24:42.846535
"""
from typing import Sequence, Union

from alembic import op


revision: str = "85215264fe9d"
down_revision: Union[str, Sequence[str], None] = "7cf4b9133b17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("pk_project_role", "projectrole", type_="primary")
    op.create_primary_key(
        "pk_project_role",
        "projectrole",
        ["project_id", "user_id", "role"],
    )


def downgrade() -> None:
    op.drop_constraint("pk_project_role", "projectrole", type_="primary")
    op.create_primary_key(
        "pk_project_role",
        "projectrole",
        ["project_id", "user_id"],
    )
