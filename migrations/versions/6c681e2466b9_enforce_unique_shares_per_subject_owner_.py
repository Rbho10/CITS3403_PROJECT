"""Enforce unique shares per subject-owner-target

Revision ID: 6c681e2466b9
Revises: 051e190be830
Create Date: 2025-05-03 23:56:43.810542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c681e2466b9'
down_revision = '051e190be830'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shared_subjects', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_shared_subject', ['subject_id', 'owner_id', 'shared_with_user_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shared_subjects', schema=None) as batch_op:
        batch_op.drop_constraint('uq_shared_subject', type_='unique')

    # ### end Alembic commands ###
