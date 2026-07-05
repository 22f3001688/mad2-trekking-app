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


class TestTrekkerBooking(unittest.TestCase):
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
        self.inactive_trekker = User(
            full_name="Inactive Trekker",
            email="inactive@example.com",
            password_hash=hash_password("password123"),
            role=Roles.TREKKER,
            is_active=False,
            is_blacklisted=False,
        )
        self.blacklisted_trekker = User(
            full_name="Blacklisted Trekker",
            email="blacklisted@example.com",
            password_hash=hash_password("password123"),
            role=Roles.TREKKER,
            is_active=True,
            is_blacklisted=True,
        )
        self.staff_user = User(
            full_name="Staff User",
            email="staff@example.com",
            password_hash=hash_password("password123"),
            role=Roles.STAFF,
            is_active=True,
            is_blacklisted=False,
        )
        db.session.add_all([self.trekker_user, self.inactive_trekker, self.blacklisted_trekker, self.staff_user])
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

    def _create_open_trek(self, **overrides):
        today = date.today()
        trek = Trek(
            trek_name=overrides.get("trek_name", "Open Trek"),
            location=overrides.get("location", "Nepal"),
            description=overrides.get("description", "Open trek"),
            difficulty=overrides.get("difficulty", "moderate"),
            duration_days=overrides.get("duration_days", 5),
            total_slots=overrides.get("total_slots", 10),
            available_slots=overrides.get("available_slots", 5),
            start_date=overrides.get("start_date", today + timedelta(days=2)),
            end_date=overrides.get("end_date", today + timedelta(days=7)),
            status=overrides.get("status", TrekStatus.OPEN),
            assigned_staff_id=overrides.get("assigned_staff_id", self.staff_user.id),
        )
        db.session.add(trek)
        db.session.commit()
        return trek

    def test_trekker_can_book_open_trek(self):
        trek = self._create_open_trek()

        response = self.client.post(
            "/api/trekker/bookings",
            json={"trek_id": trek.id},
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "Trek booked successfully")
        self.assertEqual(payload["booking"]["trek_id"], trek.id)
        self.assertEqual(payload["booking"]["status"], BookingStatus.BOOKED)
        self.assertEqual(payload["booking"]["payment_status"], "not_applicable")

        updated_trek = db.session.get(Trek, trek.id)
        self.assertEqual(updated_trek.available_slots, 4)
        self.assertEqual(Booking.query.count(), 1)

    def test_trekker_cannot_book_same_trek_twice(self):
        trek = self._create_open_trek()
        first_booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=trek.id,
            status=BookingStatus.BOOKED,
            payment_status="not_applicable",
        )
        db.session.add(first_booking)
        db.session.commit()

        response = self.client.post(
            "/api/trekker/bookings",
            json={"trek_id": trek.id},
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["message"], "You already have an active booking for this trek")

    def test_booking_rejects_inactive_or_blacklisted_trekker(self):
        trek = self._create_open_trek()

        inactive_response = self.client.post(
            "/api/trekker/bookings",
            json={"trek_id": trek.id},
            headers=self._auth_headers(self.inactive_trekker),
        )
        self.assertEqual(inactive_response.status_code, 403)
        self.assertEqual(inactive_response.get_json()["message"], "Trekker account is inactive")

        blacklisted_response = self.client.post(
            "/api/trekker/bookings",
            json={"trek_id": trek.id},
            headers=self._auth_headers(self.blacklisted_trekker),
        )
        self.assertEqual(blacklisted_response.status_code, 403)
        self.assertEqual(blacklisted_response.get_json()["message"], "Trekker account is blacklisted")

    def test_booking_rejects_closed_or_past_treks(self):
        past_trek = self._create_open_trek(start_date=date.today() - timedelta(days=1))
        closed_trek = self._create_open_trek(trek_name="Closed Trek", status=TrekStatus.CLOSED)

        past_response = self.client.post(
            "/api/trekker/bookings",
            json={"trek_id": past_trek.id},
            headers=self._auth_headers(),
        )
        self.assertEqual(past_response.status_code, 400)
        self.assertEqual(past_response.get_json()["message"], "Trek start date cannot be in the past")

        closed_response = self.client.post(
            "/api/trekker/bookings",
            json={"trek_id": closed_trek.id},
            headers=self._auth_headers(),
        )
        self.assertEqual(closed_response.status_code, 400)
        self.assertEqual(closed_response.get_json()["message"], "Trek is not open for booking")


if __name__ == "__main__":
    unittest.main()