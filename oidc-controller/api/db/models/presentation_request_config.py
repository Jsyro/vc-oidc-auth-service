from typing import List
from typing import Optional, List

from pydantic import BaseModel
from sqlmodel import Field
from sqlalchemy import Column, select, UniqueConstraint, String
from sqlalchemy.dialects.postgresql import JSON

from api.db.models.base import BaseTable
from ..session import db

class AttributeFilter(BaseModel):
    schema_id: Optional[str]
    schema_issuer_did: Optional[str]
    schema_name:Optional[str]
    schema_verion: Optional[str]
    issuer_did:Optional[str]
    credential_definition_id: Optional[str]

class RequestedAttribute(BaseModel):
    name:str
    names: List[str]
    label: Optional[str]
    restrictions: list [AttributeFilter] 

class RequestedPredicate(BaseModel):
    name:str
    label:str 
    restrictions: List[AttributeFilter]
    p_value:str
    p_type:str

class PresentationRequestConfiguration(BaseModel):
    name:str
    version:str
    requested_attributes : List[RequestedAttribute]
    requested_predicate: List[RequestedPredicate]
    



class PresentationConfiguration(BaseTable, table=True):
    pres_req_conf_id: str = Field(nullable=False, sa_column_kwargs={"unique": True})
    subject_identifier: str = Field()
    _presentatation_request_configuration: Field(default={}, sa_column=Column(JSON))

    @property
    def presentation_request_configuration(self):
        return PresentationRequestConfiguration.parse_obj(self._presentatation_request_configuration)


    @classmethod
    async def find_by_pres_req_conf_id(cls, pres_req_conf_id:str) -> "PresentationConfiguration":
        q_result = await db.execute(select(cls).where(cls.pres_req_conf_id == pres_req_conf_id))
        return q_result.scalar_one_or_none()
 