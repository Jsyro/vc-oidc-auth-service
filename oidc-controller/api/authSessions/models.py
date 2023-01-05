import uuid
from datetime import datetime, timedelta

from sqlmodel import Field
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import JSON

from api.core.models import UUIDModel, BaseSQLModel


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
    pass


class AuthSessionCreate(AuthSessionBase):
    pass


class AuthSessionPatch(AuthSessionBase):
    pass
