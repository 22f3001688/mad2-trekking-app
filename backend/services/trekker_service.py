from datetime import date

from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models.booking import Booking
from ..models.trek import Trek
from ..models.user import User
from ..utils.constants import BookingStatus, Roles, TrekStatus
from .booking_service import BookingService
from .cache_service import build_trek_browse_cache_key, cache_service, normalize_trek_browse_filters


class TrekkerService:
    def __init__(self):
        self.booking_service = BookingService()

    def get_dashboard(self, trekker_user_id):
        trekker_user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if trekker_user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        today = date.today()
        user_bookings_query = Booking.query.join(Trek).filter(Booking.user_id == trekker_user.id)

        available_open_treks = Trek.query.filter_by(status=TrekStatus.OPEN).count()
        active_bookings = (
            user_bookings_query.filter(
                Booking.status == BookingStatus.BOOKED,
                Trek.status != TrekStatus.COMPLETED,
            ).count()
        )
        completed_treks = (
            user_bookings_query.filter(
                Booking.status == BookingStatus.BOOKED,
                Trek.status == TrekStatus.COMPLETED,
            ).count()
        )
        upcoming_treks = (
            user_bookings_query.filter(
                Booking.status == BookingStatus.BOOKED,
                Trek.start_date >= today,
                Trek.status != TrekStatus.COMPLETED,
            ).count()
        )

        upcoming_bookings = (
            Booking.query.options(joinedload(Booking.trek))
            .join(Trek)
            .filter(
                Booking.user_id == trekker_user.id,
                Booking.status == BookingStatus.BOOKED,
                Trek.start_date >= today,
                Trek.status != TrekStatus.COMPLETED,
            )
            .order_by(Trek.start_date.asc(), Booking.booking_date.asc())
            .limit(5)
            .all()
        )

        next_upcoming_treks = []
        for booking in upcoming_bookings:
            trek = booking.trek
            next_upcoming_treks.append(
                {
                    "trek_name": trek.trek_name if trek else None,
                    "location": trek.location if trek else None,
                    "start_date": trek.start_date.isoformat() if trek else None,
                    "end_date": trek.end_date.isoformat() if trek else None,
                    "booking_status": booking.status,
                }
            )

        return {
            "success": True,
            "data": {
                "user_name": trekker_user.full_name,
                "available_open_treks": available_open_treks,
                "active_bookings": active_bookings,
                "completed_treks": completed_treks,
                "upcoming_treks": upcoming_treks,
                "upcoming_bookings": next_upcoming_treks,
            },
        }, 200

    def get_open_treks(self, trekker_user_id, filters=None):
        today = date.today()
        filters = filters or {}

        try:
            normalized_filters = normalize_trek_browse_filters(filters)
        except (TypeError, ValueError):
            return {"success": False, "message": "Duration must be an integer"}, 400

        cache_key = build_trek_browse_cache_key(trekker_user_id, normalized_filters, today.isoformat())
        cached_response = cache_service.get_json(cache_key)
        if cached_response is not None:
            from flask import current_app

            current_app.logger.info("Trek browse cache HIT key=%s", cache_key)
            return cached_response, 200

        from flask import current_app

        current_app.logger.info("Trek browse cache MISS key=%s", cache_key)

        booked_trek_ids = set()
        if trekker_user_id is not None:
            booked_trek_ids = {
                trek_id
                for (trek_id,) in Booking.query.filter_by(
                    user_id=trekker_user_id,
                    status=BookingStatus.BOOKED,
                ).with_entities(Booking.trek_id).all()
            }

        query = Trek.query.options(joinedload(Trek.assigned_staff)).filter(
            Trek.status == TrekStatus.OPEN,
            Trek.available_slots > 0,
            Trek.start_date >= today,
        )

        search_term = normalized_filters.get("q") or ""
        difficulty = normalized_filters.get("difficulty") or ""
        location = normalized_filters.get("location") or ""
        duration = normalized_filters.get("duration") or ""
        sort_option = normalized_filters.get("sort") or "start_asc"

        if search_term:
            query = query.filter(
                (Trek.trek_name.ilike(f"%{search_term}%"))
                | (Trek.location.ilike(f"%{search_term}%"))
                | (Trek.description.ilike(f"%{search_term}%"))
            )
        if difficulty:
            query = query.filter(Trek.difficulty == difficulty)
        if location:
            query = query.filter(Trek.location.ilike(f"%{location}%"))
        if duration:
            try:
                query = query.filter(Trek.duration_days == int(duration))
            except (TypeError, ValueError):
                return {"success": False, "message": "Duration must be an integer"}, 400

        if sort_option == "start_desc":
            query = query.order_by(Trek.start_date.desc(), Trek.id.desc())
        elif sort_option == "duration_asc":
            query = query.order_by(Trek.duration_days.asc(), Trek.start_date.asc(), Trek.id.asc())
        elif sort_option == "duration_desc":
            query = query.order_by(Trek.duration_days.desc(), Trek.start_date.asc(), Trek.id.asc())
        elif sort_option == "location_asc":
            query = query.order_by(Trek.location.asc(), Trek.start_date.asc(), Trek.id.asc())
        else:
            query = query.order_by(Trek.start_date.asc(), Trek.id.asc())

        treks = query.all()

        serialized_treks = []
        for trek in treks:
            serialized_treks.append(
                {
                    "id": trek.id,
                    "trek_name": trek.trek_name,
                    "location": trek.location,
                    "description": trek.description,
                    "difficulty": trek.difficulty,
                    "duration_days": trek.duration_days,
                    "available_slots": trek.available_slots,
                    "total_slots": trek.total_slots,
                    "start_date": trek.start_date.isoformat(),
                    "end_date": trek.end_date.isoformat(),
                    "assigned_staff_name": trek.assigned_staff.full_name if trek.assigned_staff else None,
                    "already_booked": trek.id in booked_trek_ids,
                }
            )

        response_payload = {"success": True, "data": serialized_treks}
        if cache_service.set_json(cache_key, response_payload):
            current_app.logger.info("Trek browse cache SET key=%s", cache_key)

        return response_payload, 200

    def book_trek(self, trekker_user_id, data):
        return self.booking_service.book_trek(trekker_user_id, data)

    def get_my_bookings(self, trekker_user_id):
        return self.booking_service.get_my_bookings(trekker_user_id)

    def get_booking_details(self, trekker_user_id, booking_id):
        return self.booking_service.get_booking_details(trekker_user_id, booking_id)

    def cancel_booking(self, trekker_user_id, booking_id):
        return self.booking_service.cancel_booking(trekker_user_id, booking_id)

    def get_history(self, trekker_user_id):
        return self.booking_service.get_history(trekker_user_id)

    def get_profile(self, trekker_user_id):
        trekker_user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if trekker_user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        return {
            "success": True,
            "data": {
                "id": trekker_user.id,
                "full_name": trekker_user.full_name,
                "email": trekker_user.email,
                "phone": trekker_user.phone,
                "role": trekker_user.role,
            },
        }, 200

    def update_profile(self, trekker_user_id, data):
        trekker_user = User.query.filter_by(id=trekker_user_id, role=Roles.TREKKER).first()
        if trekker_user is None:
            return {"success": False, "message": "Trekker not found"}, 404

        full_name = (data.get("full_name") or "").strip()
        phone = (data.get("phone") or "").strip()

        if not full_name:
            return {"success": False, "message": "Full name is required"}, 400
        if phone and len(phone) > 20:
            return {"success": False, "message": "Phone number must be 20 characters or less"}, 400

        trekker_user.full_name = full_name
        trekker_user.phone = phone or None
        db.session.commit()

        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": {
                "id": trekker_user.id,
                "full_name": trekker_user.full_name,
                "email": trekker_user.email,
                "phone": trekker_user.phone,
                "role": trekker_user.role,
            },
        }, 200
