import unittest
from datetime import date

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.extensions import db
from backend.models.trek import Trek
from backend.models.user import User
from backend.utils.constants import Roles, TrekStatus
from backend.utils.security import hash_password


class TestStaffUpdateTrekStatus(unittest.TestCase):
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

    def test_staff_can_update_assigned_trek_status(self):
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
        db.session.commit()

        response = self.client.put(
            f"/api/staff/treks/{trek.id}/status",
            json={"status": "closed"},
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["status"], "closed")

    def test_completed_trek_cannot_be_updated_again(self):
        trek = Trek(
            trek_name="Completed Trek",
            location="Bhutan",
            description="Completed",
            difficulty="easy",
            duration_days=4,
            total_slots=6,
            available_slots=0,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
            status=TrekStatus.COMPLETED,
            assigned_staff_id=self.staff_user.id,
        )
        db.session.add(trek)
        db.session.commit()

        response = self.client.put(
            f"/api/staff/treks/{trek.id}/status",
            json={"status": "open"},
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertIn("Completed treks cannot be changed again", payload["message"])


if __name__ == "__main__":
    unittest.main()
