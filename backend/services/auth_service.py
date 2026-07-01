import re

from flask_jwt_extended import create_access_token

from ..extensions import db
from ..models.user import User
from ..utils.constants import Roles
from ..utils.security import hash_password, verify_password


class AuthService:
    def register(self, data):
        full_name = (data.get("full_name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        confirm_password = data.get("confirm_password") or ""
        requested_role = (data.get("role") or "").strip().lower()

        if not full_name:
            return {"success": False, "message": "Full name is required"}, 400

        if not email:
            return {"success": False, "message": "Email is required"}, 400

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return {"success": False, "message": "Invalid email format"}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user is not None:
            return {"success": False, "message": "Email already exists"}, 400

        if not password:
            return {"success": False, "message": "Password is required"}, 400

        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters"}, 400

        if password != confirm_password:
            return {"success": False, "message": "Passwords do not match"}, 400

        if requested_role and requested_role != Roles.TREKKER:
            return {"success": False, "message": "Only trekker registration is allowed"}, 400

        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            is_blacklisted=False,
        )
        user.role = Roles.TREKKER

        db.session.add(user)
        db.session.commit()

        return {"success": True, "message": "Registration successful"}, 201

    def login(self, data):
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email:
            return {"success": False, "message": "Email is required"}, 400

        if not password:
            return {"success": False, "message": "Password is required"}, 400

        user = User.query.filter_by(email=email).first()
        if user is None:
            return {"success": False, "message": "Invalid email or password"}, 401

        if not verify_password(password, user.password_hash):
            return {"success": False, "message": "Invalid email or password"}, 401

        if not user.is_active:
            return {"success": False, "message": "Account is inactive"}, 403

        if user.is_blacklisted:
            return {"success": False, "message": "Account is blacklisted"}, 403

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role, "email": user.email},
        )

        return {
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "role": user.role,
                "email": user.email,
            },
            "expiration": "1 day",
        }, 200

    def logout(self):
        return {"success": True, "message": "Logout not implemented"}, 200

    def get_profile(self):
        return {"success": True, "message": "Profile not implemented"}, 200
