import unittest
from datetime import date, timedelta

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.extensions import db
from backend.models.booking import Booking
from backend.models.trek import Trek
from backend.models.user import User
from backend.utils.constants import BookingStatus, Roles, TrekStatus
from backend.utils.security import hash_password


class TestTrekkerMyBookings(unittest.TestCase):
    def setUp(self):
        self.app = create_app(type("TestConfig", (), {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret",
            "JWT_SECRET_KEY": "test-jwt-secret",
        }))
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.trekker_user = User(
            full_name="Trekker User",
            email="trekker@example.com",
            password_hash=hash_password("password123"),
            role=Roles.TREKKER,
            is_active=True,
            is_blacklisted=False,
        )
        self.other_trekker = User(
            full_name="Other Trekker",
            email="other@example.com",
            password_hash=hash_password("password123"),
            role=Roles.TREKKER,
            is_active=True,
            is_blacklisted=False,
        )
        self.staff_user = User(
            full_name="Staff User",
            email="staff@example.com",
            password_hash=hash_password("password123"),
            role=Roles.STAFF,
            is_active=True,
            is_blacklisted=False,
        )
        db.session.add_all([self.trekker_user, self.other_trekker, self.staff_user])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _auth_headers(self, user=None):
        user = user or self.trekker_user
        token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "email": user.email})
        return {"Authorization": f"Bearer {token}"}

    def _create_trek(self, **kwargs):
        today = date.today()
        trek = Trek(
            trek_name=kwargs.get("trek_name", "Trek"),
            location=kwargs.get("location", "Nepal"),
            description=kwargs.get("description", "Description"),
            difficulty=kwargs.get("difficulty", "moderate"),
            duration_days=kwargs.get("duration_days", 5),
            total_slots=kwargs.get("total_slots", 10),
            available_slots=kwargs.get("available_slots", 5),
            start_date=kwargs.get("start_date", today + timedelta(days=5)),
            end_date=kwargs.get("end_date", today + timedelta(days=10)),
            status=kwargs.get("status", TrekStatus.OPEN),
            assigned_staff_id=kwargs.get("assigned_staff_id", self.staff_user.id),
        )
        db.session.add(trek)
        db.session.commit()
        return trek

    def test_returns_only_logged_in_users_bookings_ordered_by_group(self):
        today = date.today()

        upcoming_trek = self._create_trek(
            trek_name="Upcoming Trek",
            start_date=today + timedelta(days=4),
            end_date=today + timedelta(days=8),
            status=TrekStatus.OPEN,
        )
        active_trek = self._create_trek(
            trek_name="Active Trek",
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=2),
            status=TrekStatus.OPEN,
        )
        completed_trek = self._create_trek(
            trek_name="Completed Trek",
            start_date=today - timedelta(days=10),
            end_date=today - timedelta(days=4),
            status=TrekStatus.COMPLETED,
            available_slots=0,
        )
        cancelled_trek = self._create_trek(
            trek_name="Cancelled Trek",
            start_date=today + timedelta(days=7),
            end_date=today + timedelta(days=12),
            status=TrekStatus.OPEN,
        )

        own_upcoming_booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=upcoming_trek.id,
            booking_date=today + timedelta(days=1),
            status=BookingStatus.BOOKED,
            payment_status="not_applicable",
        )
        own_active_booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=active_trek.id,
            booking_date=today - timedelta(days=3),
            status=BookingStatus.BOOKED,
            payment_status="not_applicable",
        )
        own_completed_booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=completed_trek.id,
            booking_date=today - timedelta(days=12),
            status=BookingStatus.BOOKED,
            payment_status="paid",
        )
        own_cancelled_booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=cancelled_trek.id,
            booking_date=today - timedelta(days=1),
            status=BookingStatus.CANCELLED,
            payment_status="refunded",
        )
        other_booking = Booking(
            user_id=self.other_trekker.id,
            trek_id=upcoming_trek.id,
            booking_date=today,
            status=BookingStatus.BOOKED,
            payment_status="not_applicable",
        )
        db.session.add_all([
            own_upcoming_booking,
            own_active_booking,
            own_completed_booking,
            own_cancelled_booking,
            other_booking,
        ])
        db.session.commit()

        response = self.client.get("/api/trekker/bookings", headers=self._auth_headers())

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(len(payload["data"]), 4)
        self.assertEqual(payload["data"][0]["trek_name"], "Upcoming Trek")
        self.assertEqual(payload["data"][0]["booking_group"], "upcoming")
        self.assertEqual(payload["data"][1]["trek_name"], "Active Trek")
        self.assertEqual(payload["data"][1]["booking_group"], "active")
        self.assertEqual(payload["data"][2]["trek_name"], "Completed Trek")
        self.assertEqual(payload["data"][2]["booking_group"], "completed")
        self.assertEqual(payload["data"][3]["trek_name"], "Cancelled Trek")
        self.assertEqual(payload["data"][3]["booking_group"], "cancelled")
        self.assertEqual(payload["data"][0]["assigned_staff_name"], "Staff User")

    def test_rejects_non_trekker_users(self):
        response = self.client.get("/api/trekker/bookings", headers=self._auth_headers(self.staff_user))

        self.assertEqual(response.status_code, 403)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["message"], "Forbidden")


if __name__ == "__main__":
    unittest.main()