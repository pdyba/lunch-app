"""empty message

Revision ID: 2d518985baf
Revises: b68173d492
Create Date: 2015-04-13 17:16:48.955085

"""

# revision identifiers, used by Alembic.
revision = '2d518985baf'
down_revision = 'b68173d492'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('conflicts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_by_user', sa.String(length=100), nullable=True),
    sa.Column('user_connected', sa.String(length=100), nullable=True),
    sa.Column('order_connected', sa.String(length=10), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('resolved', sa.Boolean(), nullable=True),
    sa.Column('i_know_who', sa.Boolean(), nullable=True),
    sa.Column('did_order_come', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_user'], ['user.username'], ),
    sa.ForeignKeyConstraint(['order_connected'], ['order.id'], ),
    sa.ForeignKeyConstraint(['user_connected'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('conflicts')

