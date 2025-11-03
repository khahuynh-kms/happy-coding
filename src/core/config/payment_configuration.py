from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class PayPalSettings(BaseSettings):
    api_uri: str = Field(
        "https://api-m.sandbox.paypal.com", validation_alias="PAYPAL_API_URI")
    uri: str = Field(
        "https://sandbox.paypal.com", validation_alias="PAYPAL_URI")
    email: str = Field(..., validation_alias="PAYPAL_EMAIL")
    password: str = Field(..., validation_alias="PAYPAL_PASSWORD")
    region: str = Field(..., validation_alias="PAYPAL_REGION")
    client_id: str = Field(..., validation_alias="PAYPAL_CLIENT_ID")
    client_secret: str = Field(..., validation_alias="PAYPAL_CLIENT_SECRET")
    mode: str = Field(
        "sandbox", validation_alias="PAYPAL_MODE")
    personal_sandbox_email: str = Field(
        ..., validation_alias="PAYPAL_PERSONAL_SANDBOX_EMAIL"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


class PaymentSettings(BaseSettings):
    paypal: PayPalSettings = Field(default_factory=PayPalSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )
