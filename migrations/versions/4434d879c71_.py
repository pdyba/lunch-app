"""empty message

Revision ID: 4434d879c71
Revises: 4dab1a5013a
Create Date: 2015-10-24 12:28:41.305916

"""

# revision identifiers, used by Alembic.
revision = '4434d879c71'
down_revision = '1983556ef83'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('foodevent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_by_user', sa.String(length=100), nullable=True),
    sa.Column('event_name', sa.String(length=100), nullable=True),
    sa.Column('food_type', sa.String(length=30), nullable=True),
    sa.Column('other_food_type', sa.String(length=60), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('food_company', sa.String(length=50), nullable=True),
    sa.Column('menu', sa.String(length=500), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('deadline_for_ordering', sa.DateTime(), nullable=True),
    sa.Column('eta', sa.DateTime(), nullable=True),
    sa.Column('users_orders', sa.String(length=5000), nullable=True),
    sa.ForeignKeyConstraint(['created_by_user'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('favourite_food', sa.String(length=200), nullable=True))


def downgrade():
    op.drop_column('user', 'favourite_food')
    op.drop_table('foodevent')

