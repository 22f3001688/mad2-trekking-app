import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend.celery_app import create_celery_app
    from backend.tasks.send_daily_trek_reminders import send_daily_trek_reminders
    from backend.tasks.send_monthly_admin_report import send_monthly_admin_report
else:
    from .celery_app import create_celery_app
    from .tasks.send_daily_trek_reminders import send_daily_trek_reminders
    from .tasks.send_monthly_admin_report import send_monthly_admin_report


def main():
    parser = argparse.ArgumentParser(description="Queue TrekScape scheduled Celery tasks manually for development")
    parser.add_argument("task", choices=["daily", "monthly"], help="Which scheduled task to queue")
    parser.add_argument("--timeout", type=int, default=120, help="Seconds to wait for the Celery result")
    args = parser.parse_args()

    create_celery_app()

    if args.task == "daily":
        async_result = send_daily_trek_reminders.delay()
    else:
        async_result = send_monthly_admin_report.delay()

    print(async_result.id)
    result = async_result.get(timeout=args.timeout)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
