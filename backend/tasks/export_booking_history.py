import csv
import logging
from datetime import datetime
from pathlib import Path

from ..celery_app import celery
from ..extensions import db
from ..models.booking_history_export import BookingHistoryExport
from ..services.booking_history_export_service import build_export_filename, get_export_directory
from ..services.booking_service import BookingService

logger = logging.getLogger(__name__)
booking_service = BookingService()

CSV_HEADERS = [
    "User ID",
    "Trek Name",
    "Location",
    "Booking Status",
    "Booking Date",
    "Start Date",
    "End Date",
]


@celery.task(name="trekscape.tasks.export_booking_history", bind=True)
def export_booking_history(self, user_id):
    task_id = self.request.id
    export_record = BookingHistoryExport.query.filter_by(task_id=task_id, user_id=user_id).first()
    if export_record is None:
        logger.error("Export record not found for task_id=%s user_id=%s", task_id, user_id)
        raise RuntimeError("Booking history export failed")

    export_directory = get_export_directory()
    filename = export_record.filename or build_export_filename(user_id, task_id)
    final_path = export_directory / filename
    temp_path = Path(str(final_path) + ".tmp")

    try:
        export_record.status = "STARTED"
        db.session.commit()

        history_response, status_code = booking_service.get_history_export_rows(user_id)
        if status_code != 200 or not history_response.get("success"):
            raise RuntimeError("Unable to load booking history for export")

        rows = history_response.get("data", [])
        with temp_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "User ID": row.get("user_id"),
                        "Trek Name": row.get("trek_name"),
                        "Location": row.get("location"),
                        "Booking Status": row.get("booking_status"),
                        "Booking Date": row.get("booking_date"),
                        "Start Date": row.get("start_date"),
                        "End Date": row.get("end_date"),
                    }
                )

        temp_path.replace(final_path)

        export_record.status = "SUCCESS"
        export_record.filename = filename
        export_record.completed_at = datetime.utcnow()
        export_record.error_message = None
        db.session.commit()

        return {
            "status": "success",
            "message": "Booking history export completed",
            "filename": filename,
            "user_id": user_id,
        }
    except Exception:
        db.session.rollback()
        logger.exception("Booking history export failed for task_id=%s user_id=%s", task_id, user_id)
        try:
            export_record = BookingHistoryExport.query.filter_by(task_id=task_id, user_id=user_id).first()
            if export_record is not None:
                export_record.status = "FAILURE"
                export_record.error_message = "Booking history export failed"
                db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("Failed to update export failure state for task_id=%s user_id=%s", task_id, user_id)
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                logger.exception("Failed to remove temp export file for task_id=%s user_id=%s", task_id, user_id)
        raise
