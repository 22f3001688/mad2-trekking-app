from datetime import date, datetime

from sqlalchemy import case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models.booking import Booking
from ..models.trek import Trek
from ..models.user import User
from ..utils.constants import BookingStatus, PaymentStatus, Roles, TrekStatus
from .cache_service import invalidate_trek_browse_cache


class BookingService:
    def _serialize_booking(self, booking):
        trek = booking.trek
        return {
            "id": booking.id,
            "user_id": booking.user_id,
            "trek_id": booking.trek_id,
            "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
            "status": booking.status,
            "payment_status": booking.payment_status,
            "trek": {
                "id": trek.id if trek else None,
                "trek_name": trek.trek_name if trek else None,
                "location": trek.location if trek else None,
            },
        }

    def book_trek(self, trekker_user_id, data):
        trek_id = data.get("trek_id")
        if trek_id in (None, ""):
            return {"success": False, "message": "Trek ID is required"}, 400

        try:
            trek_id = int(trek_id)
        except (TypeError, ValueError):
            return {"success": False, "message": "Trek ID must be an integer"}, 400

        user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if user is None:
            return {"success": False, "message": "Trekker not found"}, 404
        if not user.is_active:
            return {"success": False, "message": "Trekker account is inactive"}, 403
        if user.is_blacklisted:
            return {"success": False, "message": "Trekker account is blacklisted"}, 403

        today = date.today()

        try:
            trek = (
                Trek.query.options(joinedload(Trek.assigned_staff))
                .filter_by(id=trek_id)
                .with_for_update()
                .first()
            )
            if trek is None:
                return {"success": False, "message": "Trek not found"}, 404
            if trek.status != TrekStatus.OPEN:
                return {"success": False, "message": "Trek is not open for booking"}, 400
            if trek.start_date < today:
                return {"success": False, "message": "Trek start date cannot be in the past"}, 400
            if trek.available_slots <= 0:
                return {"success": False, "message": "No available slots for this trek"}, 400

            existing_booking = Booking.query.filter_by(
                user_id=user.id,
                trek_id=trek.id,
                status=BookingStatus.BOOKED,
            ).first()
            if existing_booking is not None:
                return {"success": False, "message": "You already have an active booking for this trek"}, 400

            booking = Booking(
                user_id=user.id,
                trek_id=trek.id,
                booking_date=datetime.utcnow(),
                status=BookingStatus.BOOKED,
                payment_status=PaymentStatus.NOT_APPLICABLE,
            )
            booking.trek = trek
            trek.available_slots -= 1

            db.session.add(booking)
            db.session.flush()
            serialized_booking = self._serialize_booking(booking)
            db.session.commit()
            invalidate_trek_browse_cache()

            return {
                "success": True,
                "message": "Trek booked successfully",
                "booking": serialized_booking,
            }, 201
        except IntegrityError:
            db.session.rollback()
            existing_booking = Booking.query.filter_by(
                user_id=user.id,
                trek_id=trek_id,
                status=BookingStatus.BOOKED,
            ).first()
            if existing_booking is not None:
                return {"success": False, "message": "You already have an active booking for this trek"}, 400
            return {"success": False, "message": "Unable to book trek"}, 400
        except Exception:
            db.session.rollback()
            raise

    def get_my_bookings(self, trekker_user_id):
        user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        today = date.today()

        bookings = (
            Booking.query.options(joinedload(Booking.trek).joinedload(Trek.assigned_staff))
            .join(Trek)
            .filter(Booking.user_id == user.id)
            .order_by(
                case(
                    (Booking.status == BookingStatus.CANCELLED, 3),
                    (Trek.status == TrekStatus.COMPLETED, 2),
                    (Trek.start_date >= today, 0),
                    else_=1,
                ),
                Trek.start_date.asc(),
                Booking.booking_date.asc(),
                Booking.id.asc(),
            )
            .all()
        )

        serialized_bookings = []
        for booking in bookings:
            trek = booking.trek
            if trek is None:
                continue

            if booking.status == BookingStatus.CANCELLED:
                booking_group = "cancelled"
            elif trek.status == TrekStatus.COMPLETED:
                booking_group = "completed"
            elif trek.start_date >= today:
                booking_group = "upcoming"
            else:
                booking_group = "active"

            serialized_bookings.append(
                {
                    "booking_id": booking.id,
                    "trek_id": trek.id,
                    "trek_name": trek.trek_name,
                    "location": trek.location,
                    "difficulty": trek.difficulty,
                    "duration_days": trek.duration_days,
                    "start_date": trek.start_date.isoformat(),
                    "end_date": trek.end_date.isoformat(),
                    "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
                    "booking_status": booking.status,
                    "payment_status": booking.payment_status,
                    "trek_status": trek.status,
                    "assigned_staff_name": trek.assigned_staff.full_name if trek.assigned_staff else None,
                    "booking_group": booking_group,
                }
            )

        return {"success": True, "data": serialized_bookings}, 200

    def get_booking_details(self, trekker_user_id, booking_id):
        user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        booking = (
            Booking.query.options(joinedload(Booking.trek).joinedload(Trek.assigned_staff))
            .filter(Booking.id == booking_id, Booking.user_id == user.id)
            .first()
        )
        if booking is None or booking.trek is None:
            return {"success": False, "message": "Booking not found"}, 404

        trek = booking.trek
        return {
            "success": True,
            "data": {
                "booking": {
                    "id": booking.id,
                    "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
                    "status": booking.status,
                    "payment_status": booking.payment_status,
                },
                "trek": {
                    "id": trek.id,
                    "trek_name": trek.trek_name,
                    "location": trek.location,
                    "difficulty": trek.difficulty,
                    "duration_days": trek.duration_days,
                    "start_date": trek.start_date.isoformat(),
                    "end_date": trek.end_date.isoformat(),
                    "status": trek.status,
                    "available_slots": trek.available_slots,
                    "total_slots": trek.total_slots,
                    "description": trek.description,
                },
                "assigned_staff": {
                    "id": trek.assigned_staff.id if trek.assigned_staff else None,
                    "full_name": trek.assigned_staff.full_name if trek.assigned_staff else None,
                    "email": trek.assigned_staff.email if trek.assigned_staff else None,
                    "phone": trek.assigned_staff.phone if trek.assigned_staff else None,
                },
            },
        }, 200

    def cancel_booking(self, trekker_user_id, booking_id):
        user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        today = date.today()

        try:
            booking = (
                Booking.query.options(joinedload(Booking.trek).joinedload(Trek.assigned_staff))
                .filter(Booking.id == booking_id, Booking.user_id == user.id)
                .with_for_update()
                .first()
            )
            if booking is None or booking.trek is None:
                return {"success": False, "message": "Booking not found"}, 404

            trek = booking.trek
            if booking.status != BookingStatus.BOOKED:
                return {"success": False, "message": "Only booked bookings can be cancelled"}, 400
            if trek.start_date < today:
                return {"success": False, "message": "Trek has already started"}, 400

            booking.status = BookingStatus.CANCELLED
            trek.available_slots += 1

            db.session.commit()
            invalidate_trek_browse_cache()

            return {
                "success": True,
                "message": "Booking cancelled successfully",
                "booking": {
                    "id": booking.id,
                    "status": booking.status,
                    "trek_id": trek.id,
                    "available_slots": trek.available_slots,
                },
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {"success": False, "message": "Unable to cancel booking"}, 400
        except Exception:
            db.session.rollback()
            raise

    def get_history(self, trekker_user_id):
        user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        bookings = (
            Booking.query.options(joinedload(Booking.trek).joinedload(Trek.assigned_staff))
            .join(Trek)
            .filter(
                Booking.user_id == user.id,
                Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.CANCELLED]),
            )
            .order_by(Booking.booking_date.desc(), Booking.id.desc())
            .all()
        )

        serialized_history = []
        for booking in bookings:
            trek = booking.trek
            if trek is None:
                continue
            serialized_history.append(
                {
                    "id": booking.id,
                    "trek_name": trek.trek_name,
                    "location": trek.location,
                    "start_date": trek.start_date.isoformat(),
                    "end_date": trek.end_date.isoformat(),
                    "final_status": booking.status,
                }
            )

        return {"success": True, "data": serialized_history}, 200

    def get_history_export_rows(self, trekker_user_id):
        user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        bookings = (
            Booking.query.options(joinedload(Booking.trek).joinedload(Trek.assigned_staff))
            .join(Trek)
            .filter(
                Booking.user_id == user.id,
                Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.CANCELLED]),
            )
            .order_by(Booking.booking_date.desc(), Booking.id.desc())
            .all()
        )

        export_rows = []
        for booking in bookings:
            trek = booking.trek
            if trek is None:
                continue

            export_rows.append(
                {
                    "user_id": user.id,
                    "trek_name": trek.trek_name,
                    "location": trek.location,
                    "booking_status": booking.status,
                    "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
                    "start_date": trek.start_date.isoformat(),
                    "end_date": trek.end_date.isoformat(),
                }
            )

        return {"success": True, "data": export_rows}, 200