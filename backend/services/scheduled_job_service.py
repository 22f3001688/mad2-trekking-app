from datetime import date, timedelta
from html import escape

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models.booking import Booking
from ..models.trek import Trek
from ..models.user import User
from ..utils.constants import BookingStatus, Roles, TrekStatus


class ScheduledJobService:
    def get_daily_trek_reminders(self, window_days=1):
        today = date.today()
        reminder_end_date = today + timedelta(days=window_days)

        bookings = (
            Booking.query.options(joinedload(Booking.user), joinedload(Booking.trek))
            .join(Booking.user)
            .join(Booking.trek)
            .filter(
                Booking.status == BookingStatus.BOOKED,
                Trek.start_date >= today,
                Trek.start_date <= reminder_end_date,
                User.role == Roles.TREKKER,
                User.is_active.is_(True),
                User.is_blacklisted.is_(False),
                User.email.isnot(None),
                User.email != "",
            )
            .order_by(Trek.start_date.asc(), Booking.booking_date.asc(), Booking.id.asc())
            .all()
        )

        reminder_rows = []
        seen_pairs = set()
        for booking in bookings:
            trek = booking.trek
            user = booking.user
            if trek is None or user is None:
                continue

            dedupe_key = (user.id, trek.id)
            if dedupe_key in seen_pairs:
                continue
            seen_pairs.add(dedupe_key)

            reminder_rows.append(
                {
                    "user_id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "trek_id": trek.id,
                    "trek_name": trek.trek_name,
                    "location": trek.location,
                    "difficulty": trek.difficulty,
                    "duration_days": trek.duration_days,
                    "start_date": trek.start_date,
                    "end_date": trek.end_date,
                }
            )

        return reminder_rows

    def build_daily_trek_reminder_content(self, reminder_row):
        trek_name = reminder_row["trek_name"]
        location = reminder_row["location"]
        full_name = reminder_row["full_name"]
        start_date = reminder_row["start_date"].strftime("%d %B %Y")
        end_date = reminder_row["end_date"].strftime("%d %B %Y")
        difficulty = reminder_row["difficulty"].title()
        duration_days = reminder_row["duration_days"]

        subject = f"TrekScape reminder: {trek_name} starts soon"
        text_body = (
            f"Hello {full_name},\n\n"
            f"This is a reminder that your booked trek, {trek_name}, starts soon.\n\n"
            f"Location: {location}\n"
            f"Start Date: {start_date}\n"
            f"End Date: {end_date}\n"
            f"Difficulty: {difficulty}\n"
            f"Duration: {duration_days} days\n\n"
            "Preparation tips:\n"
            "- Carry sufficient water and snacks.\n"
            "- Wear appropriate trekking shoes and clothing.\n"
            "- Keep your ID and essentials handy.\n"
            "- Arrive on time and follow trek instructions.\n\n"
            "Safe travels,\n"
            "TrekScape Team"
        )
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.5;">
            <p>Hello {escape(full_name)},</p>
            <p>This is a reminder that your booked trek starts soon.</p>
            <table cellpadding="6" cellspacing="0" style="border-collapse: collapse; margin: 16px 0; width: 100%; max-width: 640px;">
              <tr><td style="border: 1px solid #d1d5db;"><strong>Trek Name</strong></td><td style="border: 1px solid #d1d5db;">{escape(str(trek_name))}</td></tr>
              <tr><td style="border: 1px solid #d1d5db;"><strong>Location</strong></td><td style="border: 1px solid #d1d5db;">{escape(str(location))}</td></tr>
              <tr><td style="border: 1px solid #d1d5db;"><strong>Start Date</strong></td><td style="border: 1px solid #d1d5db;">{escape(start_date)}</td></tr>
              <tr><td style="border: 1px solid #d1d5db;"><strong>End Date</strong></td><td style="border: 1px solid #d1d5db;">{escape(end_date)}</td></tr>
              <tr><td style="border: 1px solid #d1d5db;"><strong>Difficulty</strong></td><td style="border: 1px solid #d1d5db;">{escape(difficulty)}</td></tr>
              <tr><td style="border: 1px solid #d1d5db;"><strong>Duration</strong></td><td style="border: 1px solid #d1d5db;">{duration_days} days</td></tr>
            </table>
            <p><strong>Preparation tips:</strong></p>
            <ul>
              <li>Carry sufficient water and snacks.</li>
              <li>Wear appropriate trekking shoes and clothing.</li>
              <li>Keep your ID and essentials handy.</li>
              <li>Arrive on time and follow trek instructions.</li>
            </ul>
            <p>Safe travels,<br />TrekScape Team</p>
          </body>
        </html>
        """.strip()
        return subject, text_body, html_body

    def get_previous_month_date_range(self, reference_date=None):
        current_date = reference_date or date.today()
        first_day_current_month = current_date.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        return first_day_previous_month, last_day_previous_month

    def get_monthly_admin_report_data(self, reference_date=None):
        start_date, end_date = self.get_previous_month_date_range(reference_date)
        report_month = end_date.strftime("%B %Y")

        completed_treks_query = Trek.query.filter(
            Trek.status == TrekStatus.COMPLETED,
            Trek.end_date >= start_date,
            Trek.end_date <= end_date,
        )

        completed_treks = completed_treks_query.count()
        total_bookings = (
            Booking.query.join(Trek)
            .filter(
                Trek.end_date >= start_date,
                Trek.end_date <= end_date,
            )
            .count()
        )
        completed_bookings = (
            Booking.query.join(Trek)
            .filter(
                Trek.end_date >= start_date,
                Trek.end_date <= end_date,
                Booking.status == BookingStatus.COMPLETED,
            )
            .count()
        )
        cancelled_bookings = (
            Booking.query.join(Trek)
            .filter(
                Trek.end_date >= start_date,
                Trek.end_date <= end_date,
                Booking.status == BookingStatus.CANCELLED,
            )
            .count()
        )
        participants = (
            db.session.query(func.count(func.distinct(Booking.user_id)))
            .join(Trek, Booking.trek_id == Trek.id)
            .filter(
                Trek.end_date >= start_date,
                Trek.end_date <= end_date,
                Booking.status != BookingStatus.CANCELLED,
            )
            .scalar()
            or 0
        )

        popular_treks = (
            db.session.query(
                Trek.id.label("trek_id"),
                Trek.trek_name.label("trek_name"),
                Trek.location.label("location"),
                func.count(Booking.id).label("booking_count"),
                func.count(func.distinct(Booking.user_id)).label("participant_count"),
            )
            .join(Booking, Booking.trek_id == Trek.id)
            .filter(
                Trek.end_date >= start_date,
                Trek.end_date <= end_date,
                Booking.status != BookingStatus.CANCELLED,
            )
            .group_by(Trek.id, Trek.trek_name, Trek.location)
            .order_by(func.count(Booking.id).desc(), Trek.trek_name.asc())
            .limit(5)
            .all()
        )

        return {
            "report_month": report_month,
            "start_date": start_date,
            "end_date": end_date,
            "treks_conducted": completed_treks,
            "participants": participants,
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "popular_treks": [
                {
                    "trek_id": item.trek_id,
                    "trek_name": item.trek_name,
                    "location": item.location,
                    "booking_count": int(item.booking_count or 0),
                    "participant_count": int(item.participant_count or 0),
                }
                for item in popular_treks
            ],
        }

    def build_monthly_admin_report_html(self, report_data):
        popular_rows = []
        for trek in report_data["popular_treks"]:
            popular_rows.append(
                "<tr>"
                f"<td style='border:1px solid #d1d5db;padding:8px;'>{escape(trek['trek_name'])}</td>"
                f"<td style='border:1px solid #d1d5db;padding:8px;'>{escape(trek['location'])}</td>"
                f"<td style='border:1px solid #d1d5db;padding:8px;text-align:center;'>{trek['booking_count']}</td>"
                f"<td style='border:1px solid #d1d5db;padding:8px;text-align:center;'>{trek['participant_count']}</td>"
                "</tr>"
            )

        summary_items = "".join(
            [
                f"<li><strong>Treks conducted:</strong> {report_data['treks_conducted']}</li>",
                f"<li><strong>Participants:</strong> {report_data['participants']}</li>",
                f"<li><strong>Total bookings:</strong> {report_data['total_bookings']}</li>",
                f"<li><strong>Completed bookings:</strong> {report_data['completed_bookings']}</li>",
                f"<li><strong>Cancelled bookings:</strong> {report_data['cancelled_bookings']}</li>",
            ]
        )

        report_month = escape(report_data["report_month"])
        return f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.5;">
            <h2 style="margin-bottom: 8px;">TrekScape Monthly Activity Report - {report_month}</h2>
            <p style="margin-top: 0;">This report summarizes TrekScape activity for the previous calendar month.</p>
            <ul style="margin-bottom: 20px;">{summary_items}</ul>
            <h3 style="margin-bottom: 8px;">Most Popular Treks</h3>
            <table cellpadding="0" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 900px;">
              <thead>
                <tr>
                  <th style="border:1px solid #d1d5db;padding:8px;text-align:left;background:#f9fafb;">Trek Name</th>
                  <th style="border:1px solid #d1d5db;padding:8px;text-align:left;background:#f9fafb;">Location</th>
                  <th style="border:1px solid #d1d5db;padding:8px;text-align:center;background:#f9fafb;">Bookings</th>
                  <th style="border:1px solid #d1d5db;padding:8px;text-align:center;background:#f9fafb;">Participants</th>
                </tr>
              </thead>
              <tbody>
                {''.join(popular_rows) if popular_rows else '<tr><td colspan="4" style="border:1px solid #d1d5db;padding:8px;">No treks were completed during this month.</td></tr>'}
              </tbody>
            </table>
          </body>
        </html>
        """.strip()

    def build_monthly_admin_report_text(self, report_data):
        lines = [
            f"TrekScape Monthly Activity Report - {report_data['report_month']}",
            "",
            f"Treks conducted: {report_data['treks_conducted']}",
            f"Participants: {report_data['participants']}",
            f"Total bookings: {report_data['total_bookings']}",
            f"Completed bookings: {report_data['completed_bookings']}",
            f"Cancelled bookings: {report_data['cancelled_bookings']}",
            "",
            "Most Popular Treks:",
        ]
        if report_data["popular_treks"]:
            for trek in report_data["popular_treks"]:
                lines.append(
                    f"- {trek['trek_name']} ({trek['location']}): {trek['booking_count']} bookings, {trek['participant_count']} participants"
                )
        else:
            lines.append("- No treks were completed during this month.")
        return "\n".join(lines)

    def get_admin_recipient_email(self):
        configured_email = (self._get_config_value("ADMIN_EMAIL") or "").strip().lower()
        if configured_email:
            matching_admin = User.query.filter_by(email=configured_email, role=Roles.ADMIN).first()
            if matching_admin is not None and matching_admin.email:
                return matching_admin.email

        admin_user = User.query.filter_by(role=Roles.ADMIN).order_by(User.created_at.asc()).first()
        if admin_user and admin_user.email:
            return admin_user.email

        return configured_email or None

    def _get_config_value(self, key):
        from flask import current_app

        return current_app.config.get(key)
