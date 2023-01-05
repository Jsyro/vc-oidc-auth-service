import logging, json
from typing import List, Dict
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends
from ..db.session import get_async_session

from ..db.models.presentation_request_config import PresentationRequestConfiguration
from ..db.session import db


logger = logging.getLogger(__name__)

router = APIRouter()


class PresentationConfigurationRequest(BaseModel):
    subject_identifier: str = Field(
        description="An attribute in the proof that is used as the OIDC User Id"
    )
    pres_req_conf_id: str
    presentatation_request_configuration: PresentationRequestConfiguration


def is_subject_id_in_presenation_request(
    subject_id: str, pres_req_conf: PresentationRequestConfiguration
):
    for req_attr in pres_req_conf.requested_attributes:
        if subject_id == req_attr.name:
            return True
        if subject_id in req_attr.names:
            return True

    return False
