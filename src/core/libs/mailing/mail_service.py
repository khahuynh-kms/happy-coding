import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ...config.config import app_settings

from .template_factory import TemplateFactory


class MailService:
    _models = []

    def __init__(
        self, smtp_host: str, smtp_port: int, username: str, password: str
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def render_template(self, model) -> str:
        """Render template with payload using TemplateFactory mapping"""
        template_builder = TemplateFactory.get_builder(model.__class__)
        return template_builder.render(model)

    def send_mail(
        self, to_email: str, model, subject: str = None,
    ) -> None:
        if model.__class__ not in self._models:
            self._models.append(model.__class__)
            print(f"[MailService] – Registered model: {model.__class__}")

        html_content = self.render_template(model)
        msg = MIMEMultipart("alternative")
        msg["From"] = self.username
        msg["To"] = to_email

        if not subject:
            template_builder = TemplateFactory.get_builder(model.__class__)
            subject = template_builder.default_subject or None

        if not subject:
            raise ValueError("Subject is required for sending email")

        msg["Subject"] = subject

        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to_email, msg.as_string())


def mail_service() -> MailService:
    ethereal_config = app_settings.mailing.ethereal

    SMTP_SERVER = ethereal_config.smtp_host
    SMTP_PORT = ethereal_config.smtp_port
    SMTP_USER = ethereal_config.smtp_user
    SMTP_PASS = ethereal_config.smtp_pass

    config = {
        "smtp_host": SMTP_SERVER,
        "smtp_port": SMTP_PORT,
        "username": SMTP_USER,
        "password": SMTP_PASS
    }
    return MailService(**config)
