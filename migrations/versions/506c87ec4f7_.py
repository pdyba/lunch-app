"""empty message

Revision ID: 506c87ec4f7
Revises: 1983556ef83
Create Date: 2015-07-01 19:38:04.571690

"""

# revision identifiers, used by Alembic.
revision = '506c87ec4f7'
down_revision = '1983556ef83'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint('conflicts_user_connected_fkey', 'conflicts', type_='foreignkey')


def downgrade():
    op.create_foreign_key('conflicts_user_connected_fkey', 'conflicts', 'user', ['user_connected'], ['username'])

