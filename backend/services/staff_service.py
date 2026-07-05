from ..extensions import db
from ..models.booking import Booking
from ..models.trek import Trek
from ..models.user import User
from ..utils.constants import Roles, TrekStatus
from sqlalchemy.orm import joinedload


class StaffService:
    def _serialize_trek(self, trek, registered_participants=None):
        return {
            "id": trek.id,
            "trek_name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration_days": trek.duration_days,
            "available_slots": trek.available_slots,
            "total_slots": trek.total_slots,
            "status": trek.status,
            "start_date": trek.start_date.isoformat(),
            "end_date": trek.end_date.isoformat(),
            **({"registered_participants": registered_participants} if registered_participants is not None else {}),
        }

    def get_dashboard(self, staff_user_id):
        staff_user = User.query.filter_by(id=staff_user_id, role=Roles.STAFF).first()
        if staff_user is None:
            return {"success": False, "message": "Staff not found"}, 404

        assigned_treks_query = Trek.query.filter_by(assigned_staff_id=staff_user.id)
        assigned_treks_count = assigned_treks_query.count()
        open_treks_count = assigned_treks_query.filter_by(status=TrekStatus.OPEN).count()
        completed_treks_count = assigned_treks_query.filter_by(status=TrekStatus.COMPLETED).count()

        total_registered_trekkers = (
            db.session.query(Booking.user_id)
            .filter(Booking.trek_id.in_(assigned_treks_query.with_entities(Trek.id)))
            .distinct()
            .count()
        )

        return {
            "success": True,
            "data": {
                "staff_name": staff_user.full_name,
                "assigned_treks": assigned_treks_count,
                "open_treks": open_treks_count,
                "completed_treks": completed_treks_count,
                "total_registered_trekkers": total_registered_trekkers,
            },
        }, 200

    def get_my_treks(self, staff_user_id):
        staff_user = User.query.filter_by(id=staff_user_id, role=Roles.STAFF).first()
        if staff_user is None:
            return {"success": False, "message": "Staff not found"}, 404

        assigned_treks = (
            Trek.query.filter_by(assigned_staff_id=staff_user.id)
            .order_by(Trek.start_date.asc(), Trek.created_at.desc())
            .all()
        )

        serialized_treks = []
        for trek in assigned_treks:
            participant_count = Booking.query.filter_by(trek_id=trek.id).count()
            serialized_treks.append(
                {
                    **self._serialize_trek(trek),
                    "registered_participants": participant_count,
                }
            )

        return {"success": True, "data": serialized_treks}, 200

    def get_trek_participants(self, staff_user_id, trek_id):
        staff_user = User.query.filter_by(id=staff_user_id, role=Roles.STAFF).first()
        if staff_user is None:
            return {"success": False, "message": "Staff not found"}, 404

        trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=staff_user.id).first()
        if trek is None:
            return {"success": False, "message": "Trek not found or not assigned to you"}, 404

        bookings = (
            Booking.query.options(joinedload(Booking.user))
            .filter_by(trek_id=trek.id)
            .order_by(Booking.booking_date.asc())
            .all()
        )

        participants = []
        for booking in bookings:
            participant_user = booking.user
            participants.append(
                {
                    "participant_name": participant_user.full_name if participant_user else None,
                    "email": participant_user.email if participant_user else None,
                    "phone": participant_user.phone if participant_user else None,
                    "booking_status": booking.status,
                    "booking_date": booking.booking_date.isoformat(),
                    "payment_status": booking.payment_status,
                }
            )

        return {"success": True, "data": participants}, 200

    def update_trek_status(self, staff_user_id, trek_id, data):
        staff_user = User.query.filter_by(id=staff_user_id, role=Roles.STAFF).first()
        if staff_user is None:
            return {"success": False, "message": "Staff not found"}, 404

        trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=staff_user.id).first()
        if trek is None:
            return {"success": False, "message": "Trek not found or not assigned to you"}, 404

        if trek.status in (TrekStatus.PENDING, TrekStatus.APPROVED):
            return {"success": False, "message": "Pending or approved treks cannot be updated by staff"}, 400
        if trek.status == TrekStatus.COMPLETED:
            return {"success": False, "message": "Completed treks cannot be changed again"}, 400

        new_status = (data.get("status") or "").strip().lower()
        allowed_statuses = {TrekStatus.OPEN, TrekStatus.CLOSED, TrekStatus.COMPLETED}
        if new_status not in allowed_statuses:
            return {"success": False, "message": "Status must be one of: open, closed, completed"}, 400

        trek.status = new_status
        db.session.commit()

        registered_participants = Booking.query.filter_by(trek_id=trek.id).count()
        return {
            "success": True,
            "message": "Trek status updated successfully",
            "data": {
                **self._serialize_trek(trek),
                "registered_participants": registered_participants,
            },
        }, 200

    def complete_trek(self, staff_user_id, trek_id):
        staff_user = User.query.filter_by(id=staff_user_id, role=Roles.STAFF).first()
        if staff_user is None:
            return {"success": False, "message": "Staff not found"}, 404

        trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=staff_user.id).first()
        if trek is None:
            return {"success": False, "message": "Trek not found or not assigned to you"}, 404

        if trek.status == TrekStatus.COMPLETED:
            return {"success": False, "message": "Trek is already completed"}, 400

        trek.status = TrekStatus.COMPLETED
        db.session.commit()

        registered_participants = Booking.query.filter_by(trek_id=trek.id).count()
        return {
            "success": True,
            "message": "Trek marked as completed successfully",
            "data": {
                **self._serialize_trek(trek),
                "registered_participants": registered_participants,
            },
        }, 200

    def update_trek_slots(self, staff_user_id, trek_id, data):
        staff_user = User.query.filter_by(id=staff_user_id, role=Roles.STAFF).first()
        if staff_user is None:
            return {"success": False, "message": "Staff not found"}, 404

        trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=staff_user.id).first()
        if trek is None:
            return {"success": False, "message": "Trek not found or not assigned to you"}, 404

        if trek.status in (TrekStatus.PENDING, TrekStatus.APPROVED):
            return {"success": False, "message": "Pending or approved treks cannot be updated by staff"}, 400

        available_slots = data.get("available_slots")
        if available_slots in (None, ""):
            return {"success": False, "message": "Available slots is required"}, 400

        try:
            available_slots = int(available_slots)
        except (TypeError, ValueError):
            return {"success": False, "message": "Available slots must be an integer"}, 400

        if available_slots < 0:
            return {"success": False, "message": "Available slots must be greater than or equal to 0"}, 400
        if available_slots > trek.total_slots:
            return {"success": False, "message": "Available slots cannot exceed total slots"}, 400

        booked_participants = trek.total_slots - trek.available_slots
        if available_slots < booked_participants:
            return {"success": False, "message": "Available slots cannot be less than booked participants"}, 400

        trek.available_slots = available_slots
        db.session.commit()

        return {
            "success": True,
            "message": "Trek slots updated successfully",
            "data": {
                **self._serialize_trek(trek, registered_participants=booked_participants),
            },
        }, 200
