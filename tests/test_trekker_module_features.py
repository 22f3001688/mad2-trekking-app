import unittest
from datetime import date, datetime, timedelta

from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.extensions import db
from backend.models.booking import Booking
from backend.models.trek import Trek
from backend.models.user import User
from backend.utils.constants import BookingStatus, Roles, TrekStatus
from backend.utils.security import hash_password


class TestTrekkerModuleFeatures(unittest.TestCase):
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
            phone="9999999999",
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

    def test_browse_filters_and_booked_state(self):
        east_trek = self._create_trek(
            trek_name="East Trail",
            location="Kathmandu",
            description="Scenic east route",
            difficulty="easy",
            duration_days=3,
            start_date=date.today() + timedelta(days=2),
            end_date=date.today() + timedelta(days=5),
        )
        west_trek = self._create_trek(
            trek_name="West Summit",
            location="Pokhara",
            description="Hard mountain climb",
            difficulty="hard",
            duration_days=7,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=17),
        )
        booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=east_trek.id,
            status=BookingStatus.BOOKED,
            payment_status="not_applicable",
        )
        db.session.add(booking)
        db.session.commit()

        response = self.client.get(
            "/api/trekker/treks?q=east&difficulty=easy&location=Kathmandu&duration=3&sort=start_asc",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(len(payload["data"]), 1)
        self.assertEqual(payload["data"][0]["trek_name"], "East Trail")
        self.assertTrue(payload["data"][0]["already_booked"])
        self.assertNotIn("West Summit", [item["trek_name"] for item in payload["data"]])

    def test_booking_details_and_cancel(self):
        trek = self._create_trek(
            trek_name="Detail Trek",
            location="Annapurna",
            start_date=date.today() + timedelta(days=3),
            end_date=date.today() + timedelta(days=8),
        )
        booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=trek.id,
            booking_date=datetime.utcnow(),
            status=BookingStatus.BOOKED,
            payment_status="not_applicable",
        )
        db.session.add(booking)
        db.session.commit()
        original_available_slots = trek.available_slots

        details_response = self.client.get(f"/api/trekker/bookings/{booking.id}", headers=self._auth_headers())
        self.assertEqual(details_response.status_code, 200)
        details_payload = details_response.get_json()
        self.assertTrue(details_payload["success"])
        self.assertEqual(details_payload["data"]["booking"]["id"], booking.id)
        self.assertEqual(details_payload["data"]["trek"]["trek_name"], "Detail Trek")
        self.assertEqual(details_payload["data"]["assigned_staff"]["full_name"], "Staff User")

        cancel_response = self.client.put(f"/api/trekker/bookings/{booking.id}/cancel", headers=self._auth_headers())
        self.assertEqual(cancel_response.status_code, 200)
        cancel_payload = cancel_response.get_json()
        self.assertTrue(cancel_payload["success"])
        self.assertEqual(cancel_payload["booking"]["status"], BookingStatus.CANCELLED)

        updated_booking = db.session.get(Booking, booking.id)
        updated_trek = db.session.get(Trek, trek.id)
        self.assertEqual(updated_booking.status, BookingStatus.CANCELLED)
        self.assertEqual(updated_trek.available_slots, original_available_slots + 1)

    def test_history_and_profile(self):
        completed_trek = self._create_trek(
            trek_name="Completed Trek",
            location="Langtang",
            start_date=date.today() - timedelta(days=12),
            end_date=date.today() - timedelta(days=8),
            status=TrekStatus.COMPLETED,
            available_slots=0,
        )
        cancelled_trek = self._create_trek(
            trek_name="Cancelled Trek",
            location="Manang",
            start_date=date.today() + timedelta(days=6),
            end_date=date.today() + timedelta(days=11),
            status=TrekStatus.OPEN,
        )
        completed_booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=completed_trek.id,
            booking_date=datetime.utcnow() - timedelta(days=20),
            status=BookingStatus.COMPLETED,
            payment_status="paid",
        )
        cancelled_booking = Booking(
            user_id=self.trekker_user.id,
            trek_id=cancelled_trek.id,
            booking_date=datetime.utcnow() - timedelta(days=1),
            status=BookingStatus.CANCELLED,
            payment_status="refunded",
        )
        db.session.add_all([completed_booking, cancelled_booking])
        db.session.commit()

        history_response = self.client.get("/api/trekker/history", headers=self._auth_headers())
        self.assertEqual(history_response.status_code, 200)
        history_payload = history_response.get_json()
        self.assertTrue(history_payload["success"])
        self.assertEqual(len(history_payload["data"]), 2)
        self.assertEqual(history_payload["data"][0]["final_status"], BookingStatus.CANCELLED)
        self.assertEqual(history_payload["data"][1]["final_status"], BookingStatus.COMPLETED)

        profile_response = self.client.get("/api/trekker/profile", headers=self._auth_headers())
        self.assertEqual(profile_response.status_code, 200)
        profile_payload = profile_response.get_json()
        self.assertTrue(profile_payload["success"])
        self.assertEqual(profile_payload["data"]["email"], self.trekker_user.email)

        update_response = self.client.put(
            "/api/trekker/profile",
            json={"full_name": "Updated Trekker", "phone": "1234567890"},
            headers=self._auth_headers(),
        )
        self.assertEqual(update_response.status_code, 200)
        update_payload = update_response.get_json()
        self.assertTrue(update_payload["success"])
        self.assertEqual(update_payload["data"]["full_name"], "Updated Trekker")
        self.assertEqual(update_payload["data"]["phone"], "1234567890")


if __name__ == "__main__":
    unittest.main()
