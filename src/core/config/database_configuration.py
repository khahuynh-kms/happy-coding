
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class MongoDBSettings(BaseSettings):
    host: str = Field("localhost", validation_alias="MONGO_HOST")
    port: int = Field(27017, validation_alias="MONGO_PORT")
    user: str = Field("user", validation_alias="MONGO_USER")
    password: str = Field("password", validation_alias="MONGO_PASS")
    db_name: str = Field("mydatabase", validation_alias="MONGO_DB_NAME")
    app_name: str = Field(
        "my_app",
        validation_alias="MONGO_APP_NAME"
    )
    uri: str = Field(
        "mongodb://localhost:27017/mydatabase",
        validation_alias="MONGO_URI"
    )

    test_uri: str = Field(
        "mongodb://localhost:27017/test",
        validation_alias="MONGO_TEST_URI"
    )
    test_db_name: str = Field(
        "happy_coding_test",
        validation_alias="MONGO_TEST_DB_NAME"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


class DatabaseSettings(BaseSettings):
    mongodb: MongoDBSettings = Field(default_factory=MongoDBSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )
