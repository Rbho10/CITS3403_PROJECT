"""empty message

Revision ID: 8b6007cd95a1
Revises: 
Create Date: 2025-05-01 04:40:40.537253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b6007cd95a1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('Subjects', 'graph_type')
    op.drop_column('Subjects', 'graph_scale')
    op.drop_column('Subjects', 'privacy')
    op.drop_column('Subjects', 'opinion_toggle')


def downgrade():
    pass
