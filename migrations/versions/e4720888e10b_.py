"""empty message

Revision ID: e4720888e10b
Revises: 58101a0b01f5
Create Date: 2025-05-01 10:39:45.478475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4720888e10b'
down_revision = '58101a0b01f5'
branch_labels = None
depends_on = None


def upgrade():
     op.drop_table("studySubjects")


def downgrade():
    pass
