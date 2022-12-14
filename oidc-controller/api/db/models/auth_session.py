import uuid
from typing import List
from datetime import datetime, timedelta
from typing import Optional, List

from api.db.models.base import BaseTable
from sqlmodel import Field

from sqlalchemy import Column, text, select
from sqlalchemy.dialects.postgresql import UUID, JSON

class AuthSession(BaseTable, table=True):
    expired_timestamp: datetime = Field(
        nullable=False, default=datetime.now() + timedelta(seconds=600)
    )
    presentation_record_id: str = Field(nullable=False)
    presentation_request_id: uuid.UUID = Field(nullable=False)
    presentation_request_satisfied: bool = Field(nullable=False, default=False)
    presentation_request: dict = Field(default={}, sa_column=Column(JSON))
    request_parameters: dict = Field(default={}, sa_column=Column(JSON))

    _presentation: str = Field(nullable=False)
