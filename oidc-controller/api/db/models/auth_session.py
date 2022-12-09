import uuid
from typing import List
from datetime import datetime
from typing import Optional, List

from api.db.models.base import BaseTable
from sqlmodel import Field, JSON


class AuthSession(BaseTable, table=True):

    expired_timestamp: datetime = Field(nullable=False)
    presentation_record_id: uuid.UUID = Field(nullable=False)
    presentation_request_id: uuid.UUID = Field(nullable=False)
    presentation_request_satisfied: bool = Field(nullable=False, default=False)
    presentation_request: str = Field()
    request_parameters: List[str] = Field(nullable=False)
    _presentation: str = Field(nullable=False)
