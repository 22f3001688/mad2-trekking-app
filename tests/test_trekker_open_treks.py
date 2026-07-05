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


class TestTrekkerOpenTreks(unittest.TestCase):
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
        self.staff_user = User(
            full_name="Assigned Staff",
            email="staff@example.com",
            password_hash=hash_password("password123"),
            role=Roles.STAFF,
            is_active=True,
            is_blacklisted=False,
        )
        db.session.add_all([self.trekker_user, self.staff_user])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _auth_headers(self, user=None):
        user = user or self.trekker_user
        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "email": user.email},
        )
        return {"Authorization": f"Bearer {token}"}

    def test_only_open_future_treks_with_available_slots_are_returned(self):
        today = date.today()

        earliest_open_trek = Trek(
            trek_name="Earliest Open Trek",
            location="Nepal",
            description="Visible trek",
            difficulty="moderate",
            duration_days=5,
            total_slots=10,
            available_slots=4,
            start_date=today + timedelta(days=1),
            end_date=today + timedelta(days=6),
            status=TrekStatus.OPEN,
            assigned_staff_id=self.staff_user.id,
        )
        later_open_trek = Trek(
            trek_name="Later Open Trek",
            location="Bhutan",
            description="Visible trek",
            difficulty="easy",
            duration_days=4,
            total_slots=8,
            available_slots=2,
            start_date=today + timedelta(days=4),
            end_date=today + timedelta(days=8),
            status=TrekStatus.OPEN,
            assigned_staff_id=None,
        )
        closed_trek = Trek(
            trek_name="Closed Trek",
            location="India",
            description="Hidden trek",
            difficulty="hard",
            duration_days=6,
            total_slots=12,
            available_slots=5,
            start_date=today + timedelta(days=2),
            end_date=today + timedelta(days=8),
            status=TrekStatus.CLOSED,
            assigned_staff_id=None,
        )
        full_open_trek = Trek(
            trek_name="Full Open Trek",
            location="Ladakh",
            description="Hidden trek",
            difficulty="easy",
            duration_days=3,
            total_slots=6,
            available_slots=0,
            start_date=today + timedelta(days=3),
            end_date=today + timedelta(days=6),
            status=TrekStatus.OPEN,
            assigned_staff_id=None,
        )
        past_open_trek = Trek(
            trek_name="Past Open Trek",
            location="Sikkim",
            description="Hidden trek",
            difficulty="easy",
            duration_days=3,
            total_slots=6,
            available_slots=4,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=2),
            status=TrekStatus.OPEN,
            assigned_staff_id=None,
        )
        db.session.add_all([
            earliest_open_trek,
            later_open_trek,
            closed_trek,
            full_open_trek,
            past_open_trek,
        ])
        db.session.commit()

        booked_trek = Booking(
            user_id=self.trekker_user.id,
            trek_id=earliest_open_trek.id,
            status=BookingStatus.BOOKED,
            payment_status="not_applicable",
        )
        db.session.add(booked_trek)
        db.session.commit()

        response = self.client.get("/api/trekker/treks", headers=self._auth_headers())

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(len(payload["data"]), 2)
        self.assertEqual(payload["data"][0]["trek_name"], "Earliest Open Trek")
        self.assertEqual(payload["data"][0]["assigned_staff_name"], "Assigned Staff")
        self.assertTrue(payload["data"][0]["already_booked"])
        self.assertEqual(payload["data"][1]["trek_name"], "Later Open Trek")
        self.assertIsNone(payload["data"][1]["assigned_staff_name"])
        self.assertFalse(payload["data"][1]["already_booked"])

    def test_trekker_treks_endpoint_rejects_non_trekker_users(self):
        staff_headers = self._auth_headers(self.staff_user)

        response = self.client.get("/api/trekker/treks", headers=staff_headers)

        self.assertEqual(response.status_code, 403)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["message"], "Forbidden")


if __name__ == "__main__":
    unittest.main()