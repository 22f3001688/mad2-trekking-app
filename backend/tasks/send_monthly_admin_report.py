import logging

from ..celery_app import celery
from ..extensions import db
from ..services.email_service import EmailService
from ..services.scheduled_job_service import ScheduledJobService

logger = logging.getLogger(__name__)


@celery.task(name="trekscape.tasks.send_monthly_admin_report")
def send_monthly_admin_report():
    service = ScheduledJobService()
    email_service = EmailService()

    try:
        report_data = service.get_monthly_admin_report_data()
        recipient_email = service.get_admin_recipient_email()
        if not recipient_email:
            logger.error("No admin recipient email is configured or available")
            return {
                "status": "failure",
                "message": "Monthly Admin report could not be sent",
            }

        html_body = service.build_monthly_admin_report_html(report_data)
        text_body = service.build_monthly_admin_report_text(report_data)
        subject = f"TrekScape Monthly Activity Report - {report_data['report_month']}"
        email_service.send_html(subject, [recipient_email], html_body=html_body, text_body=text_body)

        return {
            "status": "success",
            "report_month": report_data["report_month"],
            "treks_conducted": report_data["treks_conducted"],
            "participants": report_data["participants"],
            "message": "Monthly Admin report sent",
        }
    except Exception:
        db.session.rollback()
        logger.exception("Monthly admin report task failed")
        return {
            "status": "failure",
            "message": "Monthly Admin report failed",
        }
