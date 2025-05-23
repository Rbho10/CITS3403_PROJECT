"""Added relationship

Revision ID: 937e9b8b5a54
Revises: 36ec2d713155
Create Date: 2025-05-03 10:09:35.986361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '937e9b8b5a54'
down_revision = '36ec2d713155'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shared_subjects') as batch_op:
        # 1) drop the old user_id (and its unnamed FK)
        batch_op.drop_column('user_id')

        # 2) add the new owner_id column
        batch_op.add_column(
            sa.Column(
                'owner_id',
                sa.Integer(),
                nullable=False
            )
        )

        # 3) explicitly create a named FK on owner_id → users.id
        batch_op.create_foreign_key(
            'fk_shared_subjects_owner_id_users',    # <— your FK constraint name
            'users',                                # referent table
            ['owner_id'],                           # local cols
            ['id']                                  # remote cols
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shared_subjects') as batch_op:
        # reverse: drop owner_id and its FK, re-add user_id + FK
        batch_op.drop_constraint(
            'fk_shared_subjects_owner_id_users',
            type_='foreignkey'
        )
        batch_op.drop_column('owner_id')

        batch_op.add_column(
            sa.Column(
                'user_id',
                sa.Integer(),
                nullable=False
            )
        )
        batch_op.create_foreign_key(
            'fk_shared_subjects_user_id_users',
            'users',
            ['user_id'],
            ['id']
        )

    # ### end Alembic commands ###
