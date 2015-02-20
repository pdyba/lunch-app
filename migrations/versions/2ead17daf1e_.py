"""empty message

Revision ID: 2ead17daf1e
Revises: 51afbfc4c54
Create Date: 2015-02-06 10:42:38.158657

"""

# revision identifiers, used by Alembic.
revision = '2ead17daf1e'
down_revision = '51afbfc4c54'

from alembic import op
import sqlalchemy as sa


def upgrade():
    sample_msg = "Sample message please change me!"
    op.bulk_insert(
        'mail_text_msg',
        [
            {
                'id': 1,
                'daily_reminder': sample_msg,
                'daily_reminder_subject': sample_msg,
                'monthly_pay_summary': sample_msg,
                'pay_reminder': sample_msg,
                'pay_slacker_reminder': sample_msg,
                'info_page_text': sample_msg,
                'blocked_user_text': sample_msg,
                'ordering_is_blocked_text': sample_msg,
            }
        ]
    )
    op.bulk_insert(
        'ordering_info',
        [
            {
               'id': 1,
               'is_allowed': True,
            }
        ]
    )


def downgrade():
    pass
