import sys
from pathlib import Path

from celery import Celery
from celery.schedules import crontab

celery = Celery("trekscape")


def init_celery(app):
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_track_started=True,
        timezone=app.config["CELERY_TIMEZONE"],
        enable_utc=True,
        beat_schedule={
            "daily-trek-reminders": {
                "task": "trekscape.tasks.send_daily_trek_reminders",
                "schedule": crontab(hour=9, minute=0),
            },
            "monthly-admin-report": {
                "task": "trekscape.tasks.send_monthly_admin_report",
                "schedule": crontab(hour=8, minute=0, day_of_month=1),
            },
        },
    )

    class FlaskContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = FlaskContextTask
    from . import tasks  # noqa: F401

    app.extensions["celery"] = celery
    return celery


def create_celery_app():
    if __package__ in (None, ""):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from backend.app import create_app
    else:
        from .app import create_app

    app = create_app()
    return app.extensions["celery"]
