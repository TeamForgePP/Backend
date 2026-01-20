"""fix default bool values

Revision ID: 7cf4b9133b17
Revises: f8bbd85bbe10
Create Date: 2026-01-20 08:18:14.970366
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "7cf4b9133b17"
down_revision: Union[str, Sequence[str], None] = "f8bbd85bbe10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    report_status = sa.Enum("UPLOADING", "READY", "FAILED", name="report_status")
    report_status.create(op.get_bind(), checkfirst=True)

    op.add_column("reports", sa.Column("content_type", sa.String(length=100), nullable=True))
    op.add_column("reports", sa.Column("size_bytes", sa.BigInteger(), nullable=True))
    op.add_column("reports", sa.Column("status", report_status, nullable=False, server_default="UPLOADING"))
    op.alter_column("reports", "status", server_default=None)


def downgrade() -> None:
    op.drop_column("reports", "status")
    op.drop_column("reports", "size_bytes")
    op.drop_column("reports", "content_type")

    report_status = sa.Enum("UPLOADING", "READY", "FAILED", name="report_status")
    report_status.drop(op.get_bind(), checkfirst=True)
