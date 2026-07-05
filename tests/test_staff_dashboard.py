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


class TestStaffDashboard(unittest.TestCase):
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

    def test_staff_dashboard_returns_only_assigned_trek_stats(self):
        assigned_open_trek = Trek(
            trek_name="Assigned Open Trek",
            location="Nepal",
            description="Open trek",
            difficulty="moderate",
            duration_days=5,
            total_slots=10,
            available_slots=10,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 6),
            status=TrekStatus.OPEN,
            assigned_staff_id=self.staff_user.id,
        )
        assigned_completed_trek = Trek(
            trek_name="Assigned Completed Trek",
            location="India",
            description="Completed trek",
            difficulty="easy",
            duration_days=3,
            total_slots=8,
            available_slots=0,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 4),
            status=TrekStatus.COMPLETED,
            assigned_staff_id=self.staff_user.id,
        )
        other_trek = Trek(
            trek_name="Other Staff Trek",
            location="Bhutan",
            description="Another trek",
            difficulty="hard",
            duration_days=8,
            total_slots=12,
            available_slots=8,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 9),
            status=TrekStatus.OPEN,
            assigned_staff_id=None,
        )
        db.session.add_all([assigned_open_trek, assigned_completed_trek, other_trek])
        db.session.flush()

        user_one = User(full_name="Trekkers One", email="trekker1@example.com", password_hash=hash_password("password"), role=Roles.TREKKER, is_active=True, is_blacklisted=False)
        user_two = User(full_name="Trekkers Two", email="trekker2@example.com", password_hash=hash_password("password"), role=Roles.TREKKER, is_active=True, is_blacklisted=False)
        db.session.add_all([user_one, user_two])
        db.session.flush()

        db.session.add_all([
            Booking(user_id=user_one.id, trek_id=assigned_open_trek.id, status="confirmed", payment_status="paid"),
            Booking(user_id=user_two.id, trek_id=assigned_open_trek.id, status="confirmed", payment_status="paid"),
            Booking(user_id=user_two.id, trek_id=assigned_completed_trek.id, status="confirmed", payment_status="paid"),
            Booking(user_id=999, trek_id=other_trek.id, status="confirmed", payment_status="paid"),
        ])
        db.session.commit()

        response = self.client.get("/api/staff/dashboard", headers=self._auth_headers(self.staff_user))

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["assigned_treks"], 2)
        self.assertEqual(payload["data"]["open_treks"], 1)
        self.assertEqual(payload["data"]["completed_treks"], 1)
        self.assertEqual(payload["data"]["total_registered_trekkers"], 2)


if __name__ == "__main__":
    unittest.main()
