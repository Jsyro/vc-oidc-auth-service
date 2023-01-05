import logging, json
from typing import List, Dict
from pydantic import BaseModel, Field
from fastapi import APIRouter, Request, HTTPException

from ..db.models import PresentationConfiguration
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


@router.post("/")
async def post_pres_req_conf(
    presentation_configuration: PresentationConfigurationRequest,
):
    if not is_subject_id_in_presenation_request(
        presentation_configuration.subject_identifier,
        presentation_configuration.presentatation_request_configuration,
    ):
        raise HTTPException(
            status_code=422,
            detail="Subject Identifier not defined in presentation request configuration",
        )

    logger.info(presentation_configuration)

    pres = PresentationConfiguration(
        subject_identifier=presentation_configuration.subject_identifier,
        pres_req_conf_id=presentation_configuration.pres_req_conf_id,
        presentation_request_configuration_json=presentation_configuration.presentatation_request_configuration.dict(),
    )
    logger.info(pres)
    logger.info(pres.presentation_request_configuration_json)
    await pres.save()
    return pres


@router.get("/{pres_req_conf_id}")
async def get_pres_req_conf(pres_req_conf_id: str):
    pres = await PresentationConfiguration.find_by_pres_req_conf_id(pres_req_conf_id)
    if not pres:
        raise HTTPException(
            status_code=404, detail="PresentationConfiguration not found"
        )

    return pres


@router.delete("/{pres_req_conf_id}")
async def del_pres_req_conf(pres_req_conf_id: str):
    pres = await PresentationConfiguration.find_by_pres_req_conf_id(pres_req_conf_id)
    if not pres:
        raise HTTPException(
            status_code=404, detail="PresentationConfiguration not found"
        )
    await pres.delete()

    pass


@router.put("/{pres_req_conf_id}")
async def put_pres_req_conf(pres_req_conf_id: str):
    pres = await PresentationConfiguration.find_by_pres_req_conf_id(pres_req_conf_id)
    if not pres:
        raise HTTPException(
            status_code=404, detail="PresentationConfiguration not found"
        )

    # pres.update()
    return pres
