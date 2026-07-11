from ..celery_app import celery


@celery.task(name="trekscape.tasks.health_check")
def health_check(message):
    return {
        "status": "success",
        "message": f"Celery received: {message}",
    }
