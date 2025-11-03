from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class MailEtherealSettings(BaseSettings):
    smtp_host: str = Field(
        "smtp.ethereal.email",
        validation_alias="ETHEREAL_SMTP_HOST")
    smtp_port: int = Field(587, validation_alias="ETHEREAL_SMTP_PORT")
    smtp_user: str = Field(validation_alias="ETHEREAL_SMTP_USER")
    smtp_pass: str = Field(..., validation_alias="ETHEREAL_SMTP_PASS")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


class MailingSettings(BaseSettings):
    ethereal: MailEtherealSettings = Field(
        default_factory=MailEtherealSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )
