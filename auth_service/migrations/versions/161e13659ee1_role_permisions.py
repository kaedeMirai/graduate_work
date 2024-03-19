"""Role permisions

Revision ID: 161e13659ee1
Revises: f820c257ab1d
Create Date: 2023-12-13 22:24:19.958154

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

import uuid
import datetime


# revision identifiers, used by Alembic.
revision: str = "161e13659ee1"
down_revision: Union[str, None] = "f820c257ab1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


permissions_table = sa.table(
    "permissions",
    sa.Column("name", sa.String()),
    sa.Column("id", sa.UUID()),
    sa.Column("created_at", sa.DateTime(timezone=True)),
    sa.Column("updated_at", sa.DateTime(timezone=True)),
)


roles_table = sa.table(
    "roles",
    sa.Column("name", sa.String()),
    sa.Column("id", sa.UUID()),
    sa.Column("created_at", sa.DateTime(timezone=True)),
    sa.Column("updated_at", sa.DateTime(timezone=True)),
)


role_permissions_table = sa.table(
    "role_permissions",
    sa.Column("role_id", sa.UUID()),
    sa.Column("permission_id", sa.UUID()),
)


def upgrade() -> None:
    now = datetime.datetime.now()

    permissions_rows = [
        {
            "name": "manage_content",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "manage_users",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "comment_moderation",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "content_moderation",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "manage_reviews",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "view_statistics",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "ad_placement",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "view_ad_statistics",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "view_content",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "add_reviews",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "set_ratings",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "create_lists",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
    ]
    permissions_name_to_id = {row["name"]: row["id"] for row in permissions_rows}
    op.bulk_insert(
        table=permissions_table,
        rows=permissions_rows,
        multiinsert=True,
    )

    roles_rows = [
        {"name": "admin", "id": uuid.uuid4(), "created_at": now, "updated_at": now},
        {
            "name": "moderator",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "advertiser",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
        {
            "name": "user",
            "id": uuid.uuid4(),
            "created_at": now,
            "updated_at": now,
        },
    ]
    roles_name_to_id = {row["name"]: row["id"] for row in roles_rows}
    op.bulk_insert(table=roles_table, rows=roles_rows, multiinsert=True)

    rp_rows = [
        {
            "role_id": roles_name_to_id["admin"],
            "permission_id": permissions_name_to_id["manage_content"],
        },
        {
            "role_id": roles_name_to_id["admin"],
            "permission_id": permissions_name_to_id["manage_users"],
        },
        {
            "role_id": roles_name_to_id["admin"],
            "permission_id": permissions_name_to_id["comment_moderation"],
        },
        {
            "role_id": roles_name_to_id["admin"],
            "permission_id": permissions_name_to_id["content_moderation"],
        },
        {
            "role_id": roles_name_to_id["admin"],
            "permission_id": permissions_name_to_id["manage_reviews"],
        },
        {
            "role_id": roles_name_to_id["admin"],
            "permission_id": permissions_name_to_id["view_statistics"],
        },
        {
            "role_id": roles_name_to_id["moderator"],
            "permission_id": permissions_name_to_id["comment_moderation"],
        },
        {
            "role_id": roles_name_to_id["moderator"],
            "permission_id": permissions_name_to_id["manage_reviews"],
        },
        {
            "role_id": roles_name_to_id["advertiser"],
            "permission_id": permissions_name_to_id["ad_placement"],
        },
        {
            "role_id": roles_name_to_id["advertiser"],
            "permission_id": permissions_name_to_id["view_ad_statistics"],
        },
        {
            "role_id": roles_name_to_id["user"],
            "permission_id": permissions_name_to_id["view_content"],
        },
        {
            "role_id": roles_name_to_id["user"],
            "permission_id": permissions_name_to_id["add_reviews"],
        },
        {
            "role_id": roles_name_to_id["user"],
            "permission_id": permissions_name_to_id["set_ratings"],
        },
        {
            "role_id": roles_name_to_id["user"],
            "permission_id": permissions_name_to_id["create_lists"],
        },
    ]
    op.bulk_insert(
        table=role_permissions_table,
        rows=rp_rows,
    )


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    delete_pr = sa.delete(role_permissions_table)
    session.execute(delete_pr)
    delete_p = sa.delete(permissions_table)
    session.execute(delete_p)
    delete_r = sa.delete(roles_table)
    session.execute(delete_r)
    session.commit()
    session.close()
