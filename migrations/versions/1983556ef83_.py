"""empty message

Revision ID: 1983556ef83
Revises: 2d518985baf
Create Date: 2015-04-15 17:03:48.131499

"""

# revision identifiers, used by Alembic.
revision = '1983556ef83'
down_revision = '2d518985baf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('conflicts', sa.Column('notes', sa.String(length=500), nullable=True))
    op.add_column('conflicts', sa.Column('resolved_by', sa.String(length=200), nullable=True))


def downgrade():
    op.drop_column('conflicts', 'resolved_by')
    op.drop_column('conflicts', 'notes')
