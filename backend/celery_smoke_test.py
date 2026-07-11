import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend.celery_app import create_celery_app
    from backend.tasks.health_check import health_check
else:
    from .celery_app import create_celery_app
    from .tasks.health_check import health_check


def main():
    message = sys.argv[1] if len(sys.argv) > 1 else "smoke test"
    celery_app = create_celery_app()

    async_result = health_check.delay(message)
    print(async_result.id)

    result = async_result.get(timeout=15)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
