"""Enforce one subject name per user

Revision ID: 051e190be830
Revises: 937e9b8b5a54
Create Date: 2025-05-03 16:30:35.127560

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '051e190be830'
down_revision = '937e9b8b5a54'
branch_labels = None
depends_on = None


def upgrade():
    # ◼︎ 0) drop any stray temp table from a previous failed batch
    op.execute(text('DROP TABLE IF EXISTS _alembic_tmp_subjects'))

    # ◼︎ 1) delete duplicate subject rows (keep lowest rowid per (user_id,name))
    op.execute(text("""
        DELETE FROM subjects
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM subjects
            GROUP BY user_id, name
        );
    """))

    # ◼︎ 2) apply the unique constraint via batch_alter
    with op.batch_alter_table('subjects', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_user_subject', ['user_id','name'])


def downgrade():
    # simply drop the constraint (no need to restore the deleted rows)
    with op.batch_alter_table('subjects', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_subject', type_='unique')
