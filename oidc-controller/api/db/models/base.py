import uuid

from typing import Optional, List
from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, func, text, select, desc, String
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, VARCHAR, ARRAY

from sqlalchemy.exc import SQLAlchemyError
from ..session import async_session


class BaseModel(SQLModel):
    pass


class BaseTable(BaseModel):
    # the following are marked optional because they are generated on the server
    # these will be included in each class where we set table=true (our table classes)
    id: Optional[uuid.UUID] = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )

    def save(self, commit=True):
        async_session.session.add(self)
        if commit:
            try:
                async_session.session.commit()
            except SQLAlchemyError as e:
                async_session.session.rollback()
                raise e
