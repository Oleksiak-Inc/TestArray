"""Add execution update metadata

Revision ID: 5e23ab1f56a7
Revises: b8fe960bb225
Create Date: 2026-07-03 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5e23ab1f56a7"
down_revision: Union[str, Sequence[str], None] = "b8fe960bb225"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("executions", sa.Column("updated_by", sa.Integer(), nullable=True))
    op.add_column("executions", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("execution_updater_idx", "executions", ["updated_by"], unique=False)
    op.create_foreign_key(
        "executions_updated_by_fkey",
        "executions",
        "users",
        ["updated_by"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("executions_updated_by_fkey", "executions", type_="foreignkey")
    op.drop_index("execution_updater_idx", table_name="executions")
    op.drop_column("executions", "updated_at")
    op.drop_column("executions", "updated_by")
