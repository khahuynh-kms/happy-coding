from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from .mailing_configuration import MailingSettings
from .payment_configuration import PaymentSettings
from .database_configuration import DatabaseSettings


class AppSettings(BaseSettings):
    debug_mode: bool = Field(False, validation_alias="DEBUG_MODE")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    payment: PaymentSettings = Field(default_factory=PaymentSettings)
    mailing: MailingSettings = Field(default_factory=MailingSettings)

    base_uri: str = Field("http://localhost:8000", validation_alias="BASE_URI")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


app_settings = AppSettings()

__all__ = ["app_settings"]
