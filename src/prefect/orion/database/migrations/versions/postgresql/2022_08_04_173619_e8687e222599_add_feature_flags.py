"""add feature flags

Revision ID: e8687e222599
Revises: 97e212ea6545
Create Date: 2022-08-04 17:36:19.023686

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Text

import prefect

# revision identifiers, used by Alembic.
revision = "e8687e222599"
down_revision = "97e212ea6545"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "feature_flag",
        sa.Column(
            "id",
            prefect.orion.utilities.database.UUID(),
            server_default=sa.text("(GEN_RANDOM_UUID())"),
            nullable=False,
        ),
        sa.Column(
            "created",
            prefect.orion.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            prefect.orion.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
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
