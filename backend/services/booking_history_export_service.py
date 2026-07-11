from pathlib import Path
from uuid import uuid4

from celery.result import AsyncResult

from ..celery_app import celery
from ..extensions import db
from ..models.booking_history_export import BookingHistoryExport
from ..models.user import User
from ..utils.constants import Roles

EXPORT_DIRECTORY = Path(__file__).resolve().parent.parent / "exports"


def get_export_directory():
    EXPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    return EXPORT_DIRECTORY


def build_export_filename(user_id, task_id):
    return f"trek_history_{user_id}_{task_id[:8]}.csv"


class BookingHistoryExportService:
    def start_export(self, trekker_user_id):
        user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        task_id = uuid4().hex
        filename = build_export_filename(user.id, task_id)
        export_record = BookingHistoryExport(
            task_id=task_id,
            user_id=user.id,
            filename=filename,
            status="PENDING",
        )

        db.session.add(export_record)
        db.session.commit()

        try:
            from ..tasks.export_booking_history import export_booking_history

            export_booking_history.apply_async(args=[user.id], task_id=task_id)
        except Exception:
            db.session.rollback()
            export_record.status = "FAILURE"
            export_record.error_message = "Booking history export failed to queue"
            db.session.commit()
            return {"success": False, "message": "Unable to start booking history export"}, 503

        return {
            "success": True,
            "message": "Booking history export started",
            "data": {
                "task_id": task_id,
                "status": "PENDING",
            },
        }, 202

    def get_export_status(self, trekker_user_id, task_id):
        user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        export_record = BookingHistoryExport.query.filter_by(task_id=task_id, user_id=user.id).first()
        if export_record is None:
            return {"success": False, "message": "Export task not found"}, 404

        task_result = AsyncResult(task_id, app=celery)
        state = task_result.state

        response = {
            "success": True,
            "data": {
                "task_id": task_id,
                "status": state,
            },
        }

        if state == "SUCCESS":
            response["message"] = "Your booking history export is ready."
            response["data"]["filename"] = export_record.filename
            response["data"]["ready"] = True
        elif state == "FAILURE":
            response["message"] = "Booking history export failed."
            response["data"]["ready"] = False
        else:
            response["message"] = "Preparing your booking history export..."
            response["data"]["ready"] = False

        return response, 200

    def get_export_download(self, trekker_user_id, task_id):
        user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        export_record = BookingHistoryExport.query.filter_by(task_id=task_id, user_id=user.id).first()
        if export_record is None:
            return {"success": False, "message": "Export task not found"}, 404

        task_result = AsyncResult(task_id, app=celery)
        if task_result.state != "SUCCESS" or export_record.status != "SUCCESS":
            return {"success": False, "message": "Booking history export is not ready yet"}, 409

        export_directory = get_export_directory()
        file_path = export_directory / export_record.filename
        if not file_path.exists():
            return {"success": False, "message": "Export file not found"}, 404

        return {
            "success": True,
            "filename": export_record.filename,
            "directory": str(export_directory),
        }, 200
