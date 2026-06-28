from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..extensions import db


class Booking(db.Model):
    """Booking model for TrekScape."""

    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("user_id", "trek_id", name="uq_booking_user_trek"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trek_id = Column(Integer, ForeignKey("treks.id"), nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), nullable=False)
    payment_status = Column(String(50), default="not_applicable", nullable=False)
    completed_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="bookings", lazy=True)
    trek = relationship("Trek", back_populates="bookings", lazy=True)

    def __repr__(self):
        return f"<Booking id={self.id} user_id={self.user_id} trek_id={self.trek_id}>"
