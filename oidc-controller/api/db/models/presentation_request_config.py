from typing import List
from typing import Optional, List

import pydantic as p
import sqlmodel as sqlm
from sqlalchemy import Column, select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property

from api.db.models.base import BaseTable
from ..session import db


class AttributeFilter(p.BaseModel):
    schema_id: Optional[str]
    schema_issuer_did: Optional[str]
    schema_name: Optional[str]
    schema_verion: Optional[str]
    issuer_did: Optional[str]
    credential_definition_id: Optional[str]


class RequestedAttribute(p.BaseModel):
    name: Optional[str]
    # names: Optional[List[str]]
    label: Optional[str]
    restrictions: list[AttributeFilter]


class RequestedPredicate(p.BaseModel):
    name: str
    label: str
    restrictions: List[AttributeFilter]
    p_value: str
    p_type: str


class PresentationRequestConfiguration(p.BaseModel):
    name: str
    version: str
    requested_attributes: Optional[List[RequestedAttribute]]
    requested_predicates: Optional[List[RequestedPredicate]]


class PresentationConfiguration(BaseTable, table=True):
    pres_req_conf_id: str = sqlm.Field(
        nullable=False, sa_column_kwargs={"unique": True}
    )
    subject_identifier: str = sqlm.Field()
    presentation_request_configuration_json: dict = sqlm.Field(sa_column=Column(JSON))

    @classmethod
    async def find_by_pres_req_conf_id(
        cls, pres_req_conf_id: str
    ) -> "PresentationConfiguration":
        q_result = await db.execute(
            select(cls).where(cls.pres_req_conf_id == pres_req_conf_id)
        )
        return q_result.scalar_one_or_none()

    def generate_proof_request(self):
        result = {
            "name": "proof_requesteed",
            "version": "0.0.1",
            "requested_attributes": {},
            "requested_predicates": {},
        }
        for req_attr in self.presentation_request_configuration_json[
            "requested_attributes"
        ]:
            result["requested_attributes"][req_attr["label"]] = req_attr
        for req_pres in self.presentation_request_configuration_json[
            "requested_predicates"
        ]:
            result["requested_predicates"][req_pres["label"]] = req_pres
        return result
