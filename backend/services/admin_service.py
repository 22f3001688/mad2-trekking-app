import re
from datetime import datetime

from ..extensions import db
from ..models.booking import Booking
from ..models.staff_profile import StaffProfile
from ..models.trek import Trek
from ..models.user import User
from ..utils.constants import BookingStatus, Roles, TrekStatus
from ..utils.security import hash_password


class AdminService:
    def get_dashboard_stats(self):
        total_treks = Trek.query.count()
        total_users = User.query.count()
        total_staff = User.query.filter_by(role=Roles.STAFF).count()
        total_bookings = Booking.query.count()
        open_treks = Trek.query.filter_by(status=TrekStatus.OPEN).count()
        completed_treks = Trek.query.filter_by(status=TrekStatus.COMPLETED).count()

        return {
            "success": True,
            "data": {
                "total_treks": total_treks,
                "total_users": total_users,
                "total_staff": total_staff,
                "total_bookings": total_bookings,
                "open_treks": open_treks,
                "completed_treks": completed_treks,
            },
        }

    def _serialize_staff(self, user):
        profile = user.staff_profile
        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "role": user.role,
            "staff_profile": {
                "id": profile.id if profile else None,
                "experience_years": profile.experience_years if profile else None,
                "specialization": profile.specialization if profile else None,
                "emergency_contact": profile.emergency_contact if profile else None,
                "status": profile.status if profile else None,
            },
        }

    def get_all_staff(self):
        staff_users = User.query.filter_by(role=Roles.STAFF).order_by(User.created_at.desc()).all()
        return {"success": True, "data": [self._serialize_staff(user) for user in staff_users]}

    def get_available_staff(self):
        staff_users = (
            User.query.filter_by(role=Roles.STAFF, is_active=True, is_blacklisted=False)
            .order_by(User.full_name.asc())
            .all()
        )
        return {"success": True, "data": [self._serialize_staff(user) for user in staff_users]}

    def create_staff(self, data):
        full_name = (data.get("full_name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        phone = (data.get("phone") or "").strip() or None
        experience_years = data.get("experience_years")
        specialization = (data.get("specialization") or "").strip() or None
        emergency_contact = (data.get("emergency_contact") or "").strip() or None
        profile_status = (data.get("status") or "active").strip() or "active"

        if not full_name:
            return {"success": False, "message": "Full name is required"}, 400
        if not email:
            return {"success": False, "message": "Email is required"}, 400
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return {"success": False, "message": "Invalid email format"}, 400
        if User.query.filter_by(email=email).first() is not None:
            return {"success": False, "message": "Email already exists"}, 400
        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters"}, 400

        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            phone=phone,
            role=Roles.STAFF,
            is_active=True,
            is_blacklisted=False,
        )
        db.session.add(user)
        db.session.flush()

        profile = StaffProfile(
            user_id=user.id,
            experience_years=int(experience_years) if experience_years not in (None, "") else None,
            specialization=specialization,
            emergency_contact=emergency_contact,
            status=profile_status,
        )
        db.session.add(profile)
        db.session.commit()

        return {"success": True, "message": "Staff created successfully", "data": self._serialize_staff(user)}, 201

    def update_staff(self, staff_id, data):
        user = User.query.filter_by(id=staff_id, role=Roles.STAFF).first()
        if user is None:
            return {"success": False, "message": "Staff not found"}, 404

        full_name = (data.get("full_name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        phone = (data.get("phone") or "").strip() or None
        password = data.get("password") or ""
        experience_years = data.get("experience_years")
        specialization = (data.get("specialization") or "").strip() or None
        emergency_contact = (data.get("emergency_contact") or "").strip() or None
        profile_status = (data.get("status") or "active").strip() or "active"
        is_active = data.get("is_active")

        if full_name:
            user.full_name = full_name
        if email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user is not None and existing_user.id != user.id:
                return {"success": False, "message": "Email already exists"}, 400
            user.email = email
        if phone is not None:
            user.phone = phone
        if password:
            if len(password) < 8:
                return {"success": False, "message": "Password must be at least 8 characters"}, 400
            user.password_hash = hash_password(password)
        if is_active is not None:
            user.is_active = bool(is_active)

        profile = user.staff_profile
        if profile is None:
            profile = StaffProfile(user_id=user.id)
            db.session.add(profile)
        if experience_years not in (None, ""):
            profile.experience_years = int(experience_years)
        if specialization is not None:
            profile.specialization = specialization
        if emergency_contact is not None:
            profile.emergency_contact = emergency_contact
        if profile_status:
            profile.status = profile_status

        db.session.commit()
        return {"success": True, "message": "Staff updated successfully", "data": self._serialize_staff(user)}, 200

    def delete_staff(self, staff_id):
        user = User.query.filter_by(id=staff_id, role=Roles.STAFF).first()
        if user is None:
            return {"success": False, "message": "Staff not found"}, 404

        user.is_active = False
        db.session.commit()
        return {"success": True, "message": "Staff deactivated successfully", "data": self._serialize_staff(user)}, 200

    def get_all_treks(self, filters=None):
        query = Trek.query

        if filters is None:
            filters = {}

        search_term = (filters.get("search") or "").strip()
        difficulty = (filters.get("difficulty") or "").strip()
        status = (filters.get("status") or "").strip()

        if search_term:
            query = query.filter(
                (Trek.trek_name.ilike(f"%{search_term}%")) | (Trek.location.ilike(f"%{search_term}%"))
            )
        if difficulty:
            query = query.filter(Trek.difficulty == difficulty)
        if status:
            query = query.filter(Trek.status == status)

        treks = query.order_by(Trek.created_at.desc()).all()
        serialized_treks = []
        for trek in treks:
            assigned_staff_name = None
            if trek.assigned_staff:
                assigned_staff_name = trek.assigned_staff.full_name

            serialized_treks.append(
                {
                    "id": trek.id,
                    "trek_name": trek.trek_name,
                    "location": trek.location,
                    "difficulty": trek.difficulty,
                    "duration_days": trek.duration_days,
                    "available_slots": trek.available_slots,
                    "total_slots": trek.total_slots,
                    "status": trek.status,
                    "assigned_staff_name": assigned_staff_name,
                    "start_date": trek.start_date.isoformat(),
                    "end_date": trek.end_date.isoformat(),
                }
            )

        return {"success": True, "data": serialized_treks}

    def get_trek_by_id(self, trek_id):
        trek = Trek.query.get(trek_id)
        if trek is None:
            return {"success": False, "message": "Trek not found"}, 404

        return {
            "success": True,
            "data": {
                "id": trek.id,
                "trek_name": trek.trek_name,
                "location": trek.location,
                "description": trek.description,
                "difficulty": trek.difficulty,
                "duration_days": trek.duration_days,
                "total_slots": trek.total_slots,
                "available_slots": trek.available_slots,
                "start_date": trek.start_date.isoformat(),
                "end_date": trek.end_date.isoformat(),
                "status": trek.status,
                "assigned_staff_id": trek.assigned_staff_id,
            },
        }, 200

    def update_trek(self, trek_id, data):
        trek = Trek.query.get(trek_id)
        if trek is None:
            return {"success": False, "message": "Trek not found"}, 404

        trek_name = (data.get("trek_name") or "").strip() or trek.trek_name
        location = (data.get("location") or "").strip() or trek.location
        description = (data.get("description") or "")
        difficulty = (data.get("difficulty") or "").strip() or trek.difficulty
        duration_days = data.get("duration_days", trek.duration_days)
        total_slots = data.get("total_slots", trek.total_slots)
        start_date = data.get("start_date") or trek.start_date.isoformat()
        end_date = data.get("end_date") or trek.end_date.isoformat()
        status = (data.get("status") or "").strip() or trek.status

        if not trek_name:
            return {"success": False, "message": "Trek name is required"}, 400
        if not location:
            return {"success": False, "message": "Location is required"}, 400
        if not difficulty:
            return {"success": False, "message": "Difficulty is required"}, 400
        if int(duration_days) <= 0:
            return {"success": False, "message": "Duration must be greater than zero"}, 400
        if int(total_slots) <= 0:
            return {"success": False, "message": "Total slots must be greater than zero"}, 400

        booked_count = Booking.query.filter_by(trek_id=trek.id).count()
        if int(total_slots) < booked_count:
            return {"success": False, "message": "Total slots cannot be less than the number of booked participants"}, 400

        try:
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return {"success": False, "message": "Dates must be in YYYY-MM-DD format"}, 400

        if parsed_start_date >= parsed_end_date:
            return {"success": False, "message": "Start date must be before end date"}, 400

        old_total_slots = trek.total_slots
        trek.trek_name = trek_name
        trek.location = location
        trek.description = description or None
        trek.difficulty = difficulty
        trek.duration_days = int(duration_days)
        trek.total_slots = int(total_slots)
        trek.start_date = parsed_start_date
        trek.end_date = parsed_end_date
        trek.status = status

        if int(total_slots) != old_total_slots:
            difference = int(total_slots) - old_total_slots
            trek.available_slots = max(0, trek.available_slots + difference)

        db.session.commit()

        return {
            "success": True,
            "message": "Trek updated successfully",
            "data": {
                "id": trek.id,
                "trek_name": trek.trek_name,
                "location": trek.location,
                "description": trek.description,
                "difficulty": trek.difficulty,
                "duration_days": trek.duration_days,
                "total_slots": trek.total_slots,
                "available_slots": trek.available_slots,
                "start_date": trek.start_date.isoformat(),
                "end_date": trek.end_date.isoformat(),
                "status": trek.status,
                "assigned_staff_id": trek.assigned_staff_id,
            },
        }, 200

    def assign_staff_to_trek(self, trek_id, data):
        trek = Trek.query.get(trek_id)
        if trek is None:
            return {"success": False, "message": "Trek not found"}, 404

        staff_id = data.get("staff_id")
        if staff_id in (None, ""):
            return {"success": False, "message": "Staff selection is required"}, 400

        try:
            staff_id = int(staff_id)
        except (TypeError, ValueError):
            return {"success": False, "message": "Staff selection is invalid"}, 400

        staff_user = User.query.get(staff_id)
        if staff_user is None:
            return {"success": False, "message": "Staff not found"}, 404
        if staff_user.role != Roles.STAFF:
            return {"success": False, "message": "Selected user is not a staff member"}, 400
        if not staff_user.is_active:
            return {"success": False, "message": "Selected staff member is inactive"}, 400
        if staff_user.is_blacklisted:
            return {"success": False, "message": "Selected staff member is blacklisted"}, 400

        trek.assigned_staff_id = staff_user.id
        db.session.commit()

        return {
            "success": True,
            "message": "Staff assigned successfully",
            "data": {
                "id": trek.id,
                "trek_name": trek.trek_name,
                "assigned_staff_id": trek.assigned_staff_id,
                "assigned_staff_name": staff_user.full_name,
            },
        }, 200

    def create_trek(self, data):
        trek_name = (data.get("trek_name") or "").strip()
        location = (data.get("location") or "").strip()
        description = (data.get("description") or "").strip() or None
        difficulty = (data.get("difficulty") or "").strip()
        duration_days = data.get("duration_days")
        total_slots = data.get("total_slots")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if not trek_name:
            return {"success": False, "message": "Trek name is required"}, 400
        if not location:
            return {"success": False, "message": "Location is required"}, 400
        if not difficulty:
            return {"success": False, "message": "Difficulty is required"}, 400
        if duration_days in (None, ""):
            return {"success": False, "message": "Duration must be greater than zero"}, 400
        if int(duration_days) <= 0:
            return {"success": False, "message": "Duration must be greater than zero"}, 400
        if total_slots in (None, ""):
            return {"success": False, "message": "Total slots must be greater than zero"}, 400
        if int(total_slots) <= 0:
            return {"success": False, "message": "Total slots must be greater than zero"}, 400
        if not start_date:
            return {"success": False, "message": "Start date is required"}, 400
        if not end_date:
            return {"success": False, "message": "End date is required"}, 400

        try:
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return {"success": False, "message": "Dates must be in YYYY-MM-DD format"}, 400

        if parsed_start_date >= parsed_end_date:
            return {"success": False, "message": "Start date must be before end date"}, 400

        trek = Trek(
            trek_name=trek_name,
            location=location,
            description=description,
            difficulty=difficulty,
            duration_days=int(duration_days),
            total_slots=int(total_slots),
            available_slots=int(total_slots),
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            status=TrekStatus.PENDING,
            assigned_staff_id=None,
        )

        db.session.add(trek)
        db.session.commit()

        return {
            "success": True,
            "message": "Trek created successfully",
            "data": {
                "id": trek.id,
                "trek_name": trek.trek_name,
                "location": trek.location,
                "description": trek.description,
                "difficulty": trek.difficulty,
                "duration_days": trek.duration_days,
                "total_slots": trek.total_slots,
                "available_slots": trek.available_slots,
                "start_date": trek.start_date.isoformat(),
                "end_date": trek.end_date.isoformat(),
                "status": trek.status,
                "assigned_staff_id": trek.assigned_staff_id,
                "created_at": trek.created_at.isoformat(),
            },
        }, 201
