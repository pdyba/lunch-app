"""empty message

Revision ID: 51afbfc4c54
Revises: 3e313cf61b7
Create Date: 2015-02-05 16:03:55.123890

"""

# revision identifiers, used by Alembic.
revision = '51afbfc4c54'
down_revision = '3e313cf61b7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'ordering_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('is_allowed', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.add_column(
        'mail_text_msg',
        sa.Column('blocked_user_text', sa.String(length=800), nullable=True),
    )
    op.add_column(
        'mail_text_msg',
        sa.Column('daily_reminder_subject', sa.String(length=200), nullable=True),
    )
    op.add_column(
        'mail_text_msg',
        sa.Column('ordering_is_blocked_text', sa.String(length=800), nullable=True),
    )


def downgrade():
    op.drop_column('mail_text_msg', 'ordering_is_blocked_text')
    op.drop_column('mail_text_msg', 'daily_reminder_subject')
    op.drop_column('mail_text_msg', 'blocked_user_text')
    op.drop_table('ordering_info')
