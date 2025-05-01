"""empty message

Revision ID: 563261642fb6
Revises: 929772c2a7b7
Create Date: 2025-05-01 10:26:49.393087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '563261642fb6'
down_revision = '929772c2a7b7'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("subject_name", "studySubjects")


def downgrade():
    pass
