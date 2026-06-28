from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from ..extensions import db


class Trek(db.Model):
    """Trek model for TrekScape."""

    __tablename__ = "treks"
    __table_args__ = (
        Index("ix_treks_status", "status"),
        Index("ix_treks_difficulty", "difficulty"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    trek_name = Column(String(150), nullable=False)
    location = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), nullable=False)
    duration_days = Column(Integer, nullable=False)
    total_slots = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    assigned_staff = relationship(
        "User",
        foreign_keys="[Trek.assigned_staff_id]",
        back_populates="assigned_treks",
        lazy=True,
    )
    bookings = relationship(
        "Booking",
        back_populates="trek",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<Trek id={self.id} trek_name={self.trek_name!r}>"
