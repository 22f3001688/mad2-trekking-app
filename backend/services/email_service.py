import logging
import smtplib
from email.message import EmailMessage
from typing import Iterable

from flask import current_app

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, app_config=None):
        self.app_config = app_config or current_app.config

    def _connect(self):
        server = self.app_config["MAIL_SERVER"]
        port = int(self.app_config["MAIL_PORT"])
        use_tls = bool(self.app_config.get("MAIL_USE_TLS"))
        username = (self.app_config.get("MAIL_USERNAME") or "").strip()
        password = (self.app_config.get("MAIL_PASSWORD") or "").strip()

        smtp = smtplib.SMTP(server, port, timeout=15)
        if use_tls:
            smtp.starttls()
        if username and password:
            smtp.login(username, password)
        return smtp

    def send_message(self, subject, recipients, text_body=None, html_body=None, sender=None):
        recipient_list = self._normalize_recipients(recipients)
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = sender or self.app_config["MAIL_DEFAULT_SENDER"]
        message["To"] = ", ".join(recipient_list)

        if text_body:
            message.set_content(text_body)
        else:
            message.set_content("")

        if html_body:
            message.add_alternative(html_body, subtype="html")

        with self._connect() as smtp:
            smtp.send_message(message)

    def send_plain_text(self, subject, recipients, text_body, sender=None):
        self.send_message(subject, recipients, text_body=text_body, sender=sender)

    def send_html(self, subject, recipients, html_body, text_body="", sender=None):
        self.send_message(subject, recipients, text_body=text_body, html_body=html_body, sender=sender)

    def _normalize_recipients(self, recipients):
        if isinstance(recipients, (list, tuple, set)):
            return [recipient.strip() for recipient in recipients if str(recipient).strip()]
        if recipients is None:
            return []
        recipient = str(recipients).strip()
        return [recipient] if recipient else []
