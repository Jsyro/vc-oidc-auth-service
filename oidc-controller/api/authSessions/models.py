import uuid
from datetime import datetime, timedelta

from sqlmodel import Field
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID, JSON

from api.db.models.base import BaseSQLModel
from api.core.models import UUIDModel
from .examples import ex_hero_create, ex_hero_patch, ex_hero_read


prefix = "auth_sess"


class AuthSessionBase(BaseSQLModel):
    expired_timestamp: datetime = Field(
        nullable=False, default=datetime.now() + timedelta(seconds=600)
    )
    ver_config_id: str = Field(nullable=False)
    pres_exch_id: uuid.UUID = Field(nullable=False)
    presentation_request_satisfied: bool = Field(nullable=False, default=False)
    presentation_exchange: dict = Field(default={}, sa_column=Column(JSON))
    request_parameters: dict = Field(default={}, sa_column=Column(JSON))

    _presentation: str = Field(nullable=False)


class AuthSession(AuthSessionBase, UUIDModel, table=True):
    __tablename__ = f"{prefix}_auth_sessions"


class AuthSessionRead(AuthSessionBase, UUIDModel):
    class Config:
        schema_extra = {"example": ex_hero_read}


class AuthSessionCreate(AuthSessionBase):
    class Config:
        schema_extra = {"example": ex_hero_create}


class AuthSessionPatch(AuthSessionBase):
    # nickname: Optional[str] = sqlm.Field(max_length=255)

    class Config:
        schema_extra = {"example": ex_hero_patch}
