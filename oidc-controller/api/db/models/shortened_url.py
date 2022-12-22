from typing import List

from sqlmodel import Field
from sqlalchemy import Column, select
from sqlalchemy.dialects.postgresql import JSON

from api.db.models.base import BaseTable
from ..session import db


class ShortenedURL(BaseTable, table=True):
    url: str = Field(nullable=False)
