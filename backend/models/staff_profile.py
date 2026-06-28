from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..extensions import db


class StaffProfile(db.Model):
    """Staff profile model for TrekScape."""

    __tablename__ = "staff_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )
    experience_years = Column(Integer, nullable=True)
    specialization = Column(String(150), nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship(
        "User",
        back_populates="staff_profile",
        uselist=False,
        lazy=True,
    )

    def __repr__(self):
        return f"<StaffProfile id={self.id} user_id={self.user_id}>"
