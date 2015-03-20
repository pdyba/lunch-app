"""empty message

Revision ID: 3e313cf61b7
Revises: None
Create Date: 2015-02-03 10:22:15.942971

"""

# revision identifiers, used by Alembic.
revision = '3e313cf61b7'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'mail_text_msg',
        sa.Column('info_page_text', sa.String(length=1600), nullable=True),
    )


def downgrade():
    op.drop_column('mail_text_msg', 'info_page_text')
