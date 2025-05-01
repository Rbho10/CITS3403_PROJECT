"""empty message

Revision ID: 125a41c498d6
Revises: e4720888e10b
Create Date: 2025-05-01 11:06:11.927835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '125a41c498d6'
down_revision = 'e4720888e10b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("studySubjects",
                    sa.Column("id", sa.Integer, nullable=False),
                    sa.Column("user_id", sa.Integer, nullable=False),
                    sa.Column("subject_name", sa.String(length=30), nullable=False),
                    sa.PrimaryKeyConstraint("id"),
                    sa.ForeignKeyConstraint(["user_id"], ["users.id"])
                    )


def downgrade():
    op.drop_table('studySubjects')
