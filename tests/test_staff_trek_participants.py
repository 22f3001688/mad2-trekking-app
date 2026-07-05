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


class TestStaffTrekParticipants(unittest.TestCase):
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

    def _auth_headers(self):
        token = create_access_token(identity=str(self.staff_user.id), additional_claims={"role": self.staff_user.role, "email": self.staff_user.email})
        return {"Authorization": f"Bearer {token}"}

    def test_staff_can_view_participants_for_assigned_trek(self):
        trek = Trek(
            trek_name="Assigned Trek",
            location="Nepal",
            description="Assigned",
            difficulty="moderate",
            duration_days=5,
            total_slots=10,
            available_slots=8,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 6),
            status=TrekStatus.OPEN,
            assigned_staff_id=self.staff_user.id,
        )
        db.session.add(trek)
        db.session.flush()

        trekkers = [
            User(full_name="Alice Trekker", email="alice@example.com", password_hash=hash_password("password123"), role=Roles.TREKKER, is_active=True, is_blacklisted=False, phone="1111111111"),
            User(full_name="Bob Trekker", email="bob@example.com", password_hash=hash_password("password123"), role=Roles.TREKKER, is_active=True, is_blacklisted=False, phone="2222222222"),
        ]
        db.session.add_all(trekkers)
        db.session.flush()

        db.session.add_all([
            Booking(user_id=trekkers[0].id, trek_id=trek.id, status="booked", payment_status="paid"),
            Booking(user_id=trekkers[1].id, trek_id=trek.id, status="booked", payment_status="pending"),
        ])
        db.session.commit()

        response = self.client.get(f"/api/staff/treks/{trek.id}/participants", headers=self._auth_headers())

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(len(payload["data"]), 2)
        self.assertEqual(payload["data"][0]["participant_name"], "Alice Trekker")
        self.assertEqual(payload["data"][0]["email"], "alice@example.com")
        self.assertEqual(payload["data"][0]["phone"], "1111111111")
        self.assertEqual(payload["data"][0]["payment_status"], "paid")

    def test_staff_cannot_view_unassigned_trek_participants(self):
        trek = Trek(
            trek_name="Unassigned Trek",
            location="Bhutan",
            description="Other",
            difficulty="easy",
            duration_days=4,
            total_slots=8,
            available_slots=8,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 4),
            status=TrekStatus.OPEN,
            assigned_staff_id=None,
        )
        db.session.add(trek)
        db.session.commit()

        response = self.client.get(f"/api/staff/treks/{trek.id}/participants", headers=self._auth_headers())

        self.assertEqual(response.status_code, 404)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertIn("Trek not found or not assigned to you", payload["message"])


if __name__ == "__main__":
    unittest.main()
