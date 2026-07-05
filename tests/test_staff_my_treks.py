import unittest
from datetime import date

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.extensions import db
from backend.models.booking import Booking
from backend.models.trek import Trek
from backend.models.user import User
from backend.utils.constants import Roles, TrekStatus
from backend.utils.security import hash_password


class TestStaffMyTreks(unittest.TestCase):
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

        self.staff_user = User(
            full_name="Staff User",
            email="staff@example.com",
            password_hash=hash_password("password123"),
            role=Roles.STAFF,
            is_active=True,
            is_blacklisted=False,
        )
        db.session.add(self.staff_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _auth_headers(self, user):
        token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "email": user.email})
        return {"Authorization": f"Bearer {token}"}

    def test_staff_my_treks_returns_only_assigned_treks_in_upcoming_order(self):
        earlier_trek = Trek(
            trek_name="Earlier Trek",
            location="Nepal",
            description="Earlier",
            difficulty="moderate",
            duration_days=5,
            total_slots=10,
            available_slots=8,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 6),
            status=TrekStatus.OPEN,
            assigned_staff_id=self.staff_user.id,
        )
        later_trek = Trek(
            trek_name="Later Trek",
            location="Bhutan",
            description="Later",
            difficulty="hard",
            duration_days=7,
            total_slots=12,
            available_slots=4,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 8),
            status=TrekStatus.OPEN,
            assigned_staff_id=self.staff_user.id,
        )
        other_trek = Trek(
            trek_name="Unassigned Trek",
            location="India",
            description="Other",
            difficulty="easy",
            duration_days=3,
            total_slots=8,
            available_slots=6,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 4),
            status=TrekStatus.PENDING,
            assigned_staff_id=None,
        )
        db.session.add_all([earlier_trek, later_trek, other_trek])
        db.session.flush()

        db.session.add(Booking(user_id=1, trek_id=earlier_trek.id, status="confirmed", payment_status="paid"))
        db.session.add(Booking(user_id=2, trek_id=earlier_trek.id, status="confirmed", payment_status="paid"))
        db.session.commit()

        response = self.client.get("/api/staff/my-treks", headers=self._auth_headers(self.staff_user))

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(len(payload["data"]), 2)
        self.assertEqual(payload["data"][0]["trek_name"], "Earlier Trek")
        self.assertEqual(payload["data"][0]["registered_participants"], 2)
        self.assertEqual(payload["data"][1]["trek_name"], "Later Trek")


if __name__ == "__main__":
    unittest.main()
