from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from ..extensions import db


class User(db.Model):
    """User account model for TrekScape."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    ROLES = ("admin", "staff", "trekker")
    is_active = Column(Boolean, default=True, nullable=False)
    is_blacklisted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    bookings = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )
    staff_profile = relationship(
        "StaffProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy=True,
    )
    assigned_treks = relationship(
        "Trek",
        back_populates="assigned_staff",
        foreign_keys="[Trek.assigned_staff_id]",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<User id={self.id} full_name={self.full_name!r} email={self.email!r}>"
