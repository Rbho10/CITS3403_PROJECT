"""empty message

Revision ID: 62603dccb1f1
Revises: 125a41c498d6
Create Date: 2025-05-12 03:00:03.485568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62603dccb1f1'
down_revision = '125a41c498d6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("sessions",
                    sa.Column("id", sa.Integer, nullable=False),
                    sa.Column("subject_id", sa.Integer, nullable=False),
                    sa.Column("user_id", sa.Integer, nullable=False),
                    sa.Column("subject_name", sa.String, nullable=False),
                    sa.Column("date", sa.Date, nullable=False),
                    sa.Column("study_duration", sa.Integer, nullable=False),
                    sa.Column("study_break", sa.Integer),
                    sa.Column("environment", sa.String),
                    sa.Column("energy_level_before", sa.Integer),
                    sa.Column("energy_level_after", sa.Integer),
                    sa.Column("difficulty", sa.Integer),
                    sa.Column("progress", sa.String),    
                    sa.PrimaryKeyConstraint("id"),
                    sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
                    sa.ForeignKeyConstraint(["subject_id"], ["studySubjects.id"]),
                    sa.ForeignKeyConstraint(["subject_name"], ["studySubjects.subject_name"]),
                    )


def downgrade():
    op.drop_table("sessions")