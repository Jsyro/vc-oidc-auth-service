from typing import List
from typing import Optional, List, Dict
import random
import pydantic as p
import sqlmodel as sqlm
from sqlalchemy import Column, select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property

from api.db.models.base import BaseSQLModel
from .examples import ex_hero_create, ex_hero_patch, ex_hero_read


prefix = "ver_conf"


class VerificationConfigBase(BaseSQLModel):
    ver_config_id: str = sqlm.Field(primary_key=True)
    subject_identifier: str = sqlm.Field()
    proof_request: dict = sqlm.Field(sa_column=Column(JSON))

    def generate_proof_request(self):
        result = {
            "name": "proof_requested",
            "version": "0.0.1",
            "requested_attributes": {},
            "requested_predicates": {},
        }
        for i, req_attr in enumerate(self.proof_request["requested_attributes"]):
            label = req_attr.get("label") or "req_attr_" + str(i)
            result["requested_attributes"][label] = req_attr
        for req_pred in self.proof_request["requested_predicates"]:
            label = req_pred.get("label") or "req_pred_" + str(i)
            result["requested_predicates"][label] = req_pred
        return result


class VerificationConfig(VerificationConfigBase, table=True):
    __tablename__ = f"{prefix}_ver_configs"


class VerificationConfigRead(VerificationConfigBase):
    class Config:
        schema_extra = {"example": ex_hero_read}


class VerificationConfigCreate(VerificationConfigBase):
    class Config:
        schema_extra = {"example": ex_hero_create}


class VerificationConfigPatch(VerificationConfigBase):
    # nickname: Optional[str] = sqlm.Field(max_length=255)

    class Config:
        schema_extra = {"example": ex_hero_patch}
