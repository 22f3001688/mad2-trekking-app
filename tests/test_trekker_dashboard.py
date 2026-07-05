import unittest
from datetime import date

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.extensions import db
from backend.models.booking import Booking
from backend.models.trek import Trek
from backend.models.user import User
from backend.utils.constants import BookingStatus, Roles, TrekStatus
from backend.utils.security import hash_password


class TestTrekkerDashboard(unittest.TestCase):
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
        db.session.add(self.trekker_user)
        db.session.commit()

        self.other_trekker_user = User(
            full_name="Other Trekker",
            email="other.trekker@example.com",
            password_hash=hash_password("password123"),
            role=Roles.TREKKER,
            is_active=True,
            is_blacklisted=False,
        )
        db.session.add(self.other_trekker_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _auth_headers(self):
        token = create_access_token(identity=str(self.trekker_user.id), additional_claims={"role": self.trekker_user.role, "email": self.trekker_user.email})
        return {"Authorization": f"Bearer {token}"}

    def test_trekker_dashboard_returns_user_specific_stats_and_upcoming_bookings(self):
        open_trek = Trek(
            trek_name="Open Trek",
            location="Nepal",
            description="Open",
            difficulty="moderate",
            duration_days=5,
            total_slots=10,
            available_slots=10,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 6),
            status=TrekStatus.OPEN,
            assigned_staff_id=None,
        )
        another_open_trek = Trek(
            trek_name="Another Open Trek",
            location="Bhutan",
            description="Open",
            difficulty="easy",
            duration_days=4,
            total_slots=8,
            available_slots=8,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 5),
            status=TrekStatus.OPEN,
            assigned_staff_id=None,
        )
        future_completed_trek = Trek(
            trek_name="Completed Trek",
            location="India",
            description="Completed",
            difficulty="hard",
            duration_days=6,
            total_slots=12,
            available_slots=0,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status=TrekStatus.COMPLETED,
            assigned_staff_id=None,
        )
        past_completed_trek = Trek(
            trek_name="Past Completed Trek",
            location="Ladakh",
            description="Done",
            difficulty="easy",
            duration_days=3,
            total_slots=6,
            available_slots=0,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 4),
            status=TrekStatus.COMPLETED,
            assigned_staff_id=None,
        )
        db.session.add_all([open_trek, another_open_trek, future_completed_trek, past_completed_trek])
        db.session.flush()

        upcoming_one = Booking(
            user_id=self.trekker_user.id,
            trek_id=open_trek.id,
            status=BookingStatus.BOOKED,
            payment_status="paid",
        )
        upcoming_two = Booking(
            user_id=self.trekker_user.id,
            trek_id=another_open_trek.id,
            status=BookingStatus.BOOKED,
            payment_status="paid",
        )
        completed_booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=future_completed_trek.id,
            status=BookingStatus.BOOKED,
            payment_status="paid",
        )
        past_completed_booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=past_completed_trek.id,
            status=BookingStatus.BOOKED,
            payment_status="paid",
        )
        cancelled_booking = Booking(
            user_id=self.other_trekker_user.id,
            trek_id=another_open_trek.id,
            status=BookingStatus.CANCELLED,
            payment_status="refunded",
        )
        db.session.add_all([upcoming_one, upcoming_two, completed_booking, past_completed_booking, cancelled_booking])
        db.session.commit()

        response = self.client.get("/api/trekker/dashboard", headers=self._auth_headers())

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["available_open_treks"], 2)
        self.assertEqual(payload["data"]["active_bookings"], 2)
        self.assertEqual(payload["data"]["completed_treks"], 2)
        self.assertEqual(payload["data"]["upcoming_treks"], 2)
        self.assertEqual(len(payload["data"]["upcoming_bookings"]), 2)
        self.assertEqual(payload["data"]["upcoming_bookings"][0]["trek_name"], "Open Trek")


if __name__ == "__main__":
    unittest.main()
