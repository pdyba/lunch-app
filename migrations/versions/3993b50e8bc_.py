"""empty message

Revision ID: 3993b50e8bc
Revises: 7c8354fe7e
Create Date: 2015-02-10 10:47:40.922069

"""

# revision identifiers, used by Alembic.
revision = '3993b50e8bc'
down_revision = '7c8354fe7e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('rate_timestamp', sa.Date(), nullable=True))


def downgrade():
    op.drop_column('user', 'rate_timestamp')
