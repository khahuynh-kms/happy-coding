from datetime import datetime, timezone
from beanie import Document, before_event, Insert, Replace, SaveChanges
from pydantic import BaseModel, ConfigDict, Field


class BaseDocument(Document):
    class Settings:
        is_root = False
        name = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class TimestampMixin(BaseModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class TimestampDocument(BaseDocument, TimestampMixin):
    @before_event([Insert])
    def set_created_at(self):
        """Set timestamps before insert."""
        now = datetime.now(timezone.utc)
        if not self.created_at:
            self.created_at = now
        self.updated_at = now

    @before_event([Replace, SaveChanges])
    def set_updated_at(self):
        """Update timestamp before changes."""
        self.updated_at = datetime.now(timezone.utc)
