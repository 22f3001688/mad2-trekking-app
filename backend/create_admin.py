import os
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.utils.constants import Roles


def main():
    app = create_app()
    with app.app_context():
        admin_name = os.getenv("ADMIN_NAME", "").strip()
        admin_email = os.getenv("ADMIN_EMAIL", "").strip()
        admin_password = os.getenv("ADMIN_PASSWORD", "").strip()

        if not admin_name or not admin_email or not admin_password:
            print(
                "Admin credentials are incomplete. Please set ADMIN_NAME, ADMIN_EMAIL, and ADMIN_PASSWORD."
            )
            return

        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin is not None:
            print(f"Admin already exists with email: {admin_email}")
            return

        admin_user = User(
            full_name=admin_name,
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            is_active=True,
            is_blacklisted=False,
        )

        if "role" in User.__table__.columns:
            admin_user.role = Roles.ADMIN
        else:
            setattr(admin_user, "role", Roles.ADMIN)

        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin created successfully: {admin_email}")


if __name__ == "__main__":
    main()
