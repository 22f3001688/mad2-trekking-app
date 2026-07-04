import unittest
from datetime import date

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.extensions import db
from backend.models.trek import Trek
from backend.models.user import User
from backend.utils.constants import Roles, TrekStatus
from backend.utils.security import hash_password


class TestAdminAssignStaff(unittest.TestCase):
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

        self.admin_user = User(
            full_name="Admin User",
            email="admin@example.com",
            password_hash=hash_password("password123"),
            role=Roles.ADMIN,
            is_active=True,
            is_blacklisted=False,
        )
        db.session.add(self.admin_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _auth_headers(self):
        token = create_access_token(identity=str(self.admin_user.id), additional_claims={"role": self.admin_user.role, "email": self.admin_user.email})
        return {"Authorization": f"Bearer {token}"}

    def test_admin_can_assign_active_staff_to_trek(self):
        trek = Trek(
            trek_name="Everest Base Camp",
            location="Nepal",
            description="Classic trek",
            difficulty="moderate",
            duration_days=7,
            total_slots=10,
            available_slots=10,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 8),
            status=TrekStatus.PENDING,
            assigned_staff_id=None,
        )
        db.session.add(trek)

        staff = User(
            full_name="Staff One",
            email="staff@example.com",
            password_hash=hash_password("password123"),
            role=Roles.STAFF,
            is_active=True,
            is_blacklisted=False,
        )
        db.session.add(staff)
        db.session.commit()

        response = self.client.put(
            f"/api/admin/treks/{trek.id}/assign-staff",
            json={"staff_id": staff.id},
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["assigned_staff_name"], "Staff One")


if __name__ == "__main__":
    unittest.main()
