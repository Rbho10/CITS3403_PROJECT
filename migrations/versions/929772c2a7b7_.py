"""empty message

Revision ID: 929772c2a7b7
Revises: 08813081adb7
Create Date: 2025-05-01 10:14:01.530314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '929772c2a7b7'
down_revision = '08813081adb7'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("subject_name", "studySubjects")


def downgrade():
    pass
