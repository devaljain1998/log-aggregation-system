from pydantic import BaseModel, field_validator
from typing import Literal
from datetime import datetime


class LogEntry(BaseModel):
    timestamp: str
    level: Literal["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
    message: str
    service: str

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ValueError(
                'timestamp must be in the format "YYYY-MM-DDTHH:MM:SSZ"'
            )
        return v
