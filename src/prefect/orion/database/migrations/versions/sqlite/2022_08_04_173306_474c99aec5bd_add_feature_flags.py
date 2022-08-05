"""add feature flags

Revision ID: 474c99aec5bd
Revises: 24bb2e4a195c
Create Date: 2022-08-04 17:33:06.793159

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Text

import prefect

# revision identifiers, used by Alembic.
revision = "474c99aec5bd"
down_revision = "24bb2e4a195c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "feature_flag",
        sa.Column(
            "id",
            prefect.orion.utilities.database.UUID(),
            server_default=sa.text(
                "(\n    (\n        lower(hex(randomblob(4))) \n        || '-' \n        || lower(hex(randomblob(2))) \n        || '-4' \n        || substr(lower(hex(randomblob(2))),2) \n        || '-' \n        || substr('89ab',abs(random()) % 4 + 1, 1) \n        || substr(lower(hex(randomblob(2))),2) \n        || '-' \n        || lower(hex(randomblob(6)))\n    )\n    )"
            ),
            nullable=False,
        ),
        sa.Column(
            "created",
            prefect.orion.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("(strftime('%Y-%m-%d %H:%M:%f000', 'now'))"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            prefect.orion.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("(strftime('%Y-%m-%d %H:%M:%f000', 'now'))"),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "data",
            prefect.orion.utilities.database.JSON(astext_type=Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_feature_flag")),
    )

    op.create_index(op.f("ix_feature_flag_name"), "feature_flag", ["name"], unique=True)


def downgrade():
    op.drop_index("ix_feature_flag_name", table_name="feature_flag")
    op.drop_table("feature_flag")
