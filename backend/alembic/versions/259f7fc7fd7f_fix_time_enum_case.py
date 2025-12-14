
"""fix_time_enum_case

Revision ID: 259f7fc7fd7f
Revises: 415652875aeb
Create Date: 2025-12-14 15:22:26.440869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '259f7fc7fd7f'
down_revision = '415652875aeb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Manually alter the column to use uppercase enum values
    op.execute("ALTER TABLE subscriptions MODIFY COLUMN time ENUM('MONTHLY', 'YEARLY', 'LIFETIME') NOT NULL")


def downgrade() -> None:
    # Revert to original casing
    op.execute("ALTER TABLE subscriptions MODIFY COLUMN time ENUM('Monthly', 'Yearly', 'Lifetime') NOT NULL")
