import sched
import time
import datetime

from flask.ext.mail import Message

from .main import mail
from .models import User, MailText

time_handler = sched.scheduler(time.time, time.sleep)
the_time = datetime.datetime.combine(
    datetime.date.today(),
    datetime.time(10, 28),
)
job_time = time.mktime(the_time.timetuple())


def send_daily_reminder():
    users = User.query.filter(User.i_want_daily_reminder is True).all
    message_text = MailText.query.first()
    with mail.connect() as conn:
        for user in users:
            msg = Message(
                'LunchApp Daily Reminder for {}'.format(datetime.date.today()),
                recipients=[user.username],
                )
            msg.body = message_text.daily_reminder
            conn.send(msg)


def time_events_handler():
    time_handler.enterabs(job_time, 1, send_daily_reminder)
    time_handler.run()
    print("\n\n\n\n\n\n\n !!! JOB DONE !!! \n\n\n\n\n\n\n")
