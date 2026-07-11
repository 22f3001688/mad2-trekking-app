import logging

from ..celery_app import celery
from ..extensions import db
from ..services.email_service import EmailService
from ..services.scheduled_job_service import ScheduledJobService

logger = logging.getLogger(__name__)


@celery.task(name="trekscape.tasks.send_daily_trek_reminders")
def send_daily_trek_reminders():
    service = ScheduledJobService()
    email_service = EmailService()
    sent_count = 0
    failed_count = 0

    try:
        reminder_rows = service.get_daily_trek_reminders(window_days=1)
        for reminder_row in reminder_rows:
            try:
                subject, text_body, html_body = service.build_daily_trek_reminder_content(reminder_row)
                email_service.send_html(subject, [reminder_row["email"]], html_body=html_body, text_body=text_body)
                sent_count += 1
            except Exception:
                failed_count += 1
                logger.exception(
                    "Failed to send trek reminder email for user_id=%s trek_id=%s",
                    reminder_row.get("user_id"),
                    reminder_row.get("trek_id"),
                )

        return {
            "status": "success",
            "sent_count": sent_count,
            "failed_count": failed_count,
            "message": "Daily trek reminders processed",
        }
    except Exception:
        db.session.rollback()
        logger.exception("Daily trek reminders task failed")
        return {
            "status": "failure",
            "sent_count": sent_count,
            "failed_count": failed_count,
            "message": "Daily trek reminders failed",
        }
