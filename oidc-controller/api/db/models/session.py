import uuid
from typing import List
from datetime import datetime
from typing import Optional, List

from api.db.models.base import BaseModel, BaseTable
from sqlmodel import Field, JSON


class OIDCSession(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: uuid.UUID = Field(primary_key=True)
    expired_timestamp: datetime = Field(nullable=False)
    presentation_record_id: uuid.UUID = Field(nullable=False)
    presentation_request_id: uuid.UUID = Field(nullable=False)
    presentation_request_satisfied: bool = Field(nullable=False, default=False)
    presentation_request: JSON = Field()
    request_parameters: List[str] = Field(nullable=False)
    _presenation: JSON = Field(nullable=False)
