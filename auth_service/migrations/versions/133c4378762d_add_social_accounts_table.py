"""Add Social accounts table

Revision ID: 133c4378762d
Revises: 161e13659ee1
Create Date: 2023-12-14 12:10:44.355701

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "133c4378762d"
down_revision: Union[str, None] = "161e13659ee1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "social_account",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("social_id", sa.Text, nullable=False),
        sa.Column("social_email", sa.Text, nullable=True),
        sa.Column("social_name", sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("social_id", "social_name", name="social_pk"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_social_account_id", "social_account", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_social_account_id"), "social_account")
    op.drop_table("social_account")
