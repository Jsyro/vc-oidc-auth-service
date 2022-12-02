import logging
from typing import List, Dict

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from oic.oic.message import (
    AuthorizationRequest,
    AccessTokenRequest,
    AuthorizationResponse,
    AuthorizationErrorResponse,
)
from pydantic import BaseModel
from ..core.acapy import AcapyClient


ChallengePollUri = "/vc/connect/poll"
AuthorizeCallbackUri = "/vc/connect/callback"
VerifiedCredentialAuthorizeUri = "/vc/connect/authorize"
VerifiedCredentialTokenUri = "/vc/connect/token"

logger = logging.getLogger(__name__)

router = APIRouter()


class ServiceDecorator(BaseModel):
    recipient_keys: List[str]
    routing_keys: List[str]
    service_endpoint: str


class PresentationAttachment(BaseModel):
    id: str
    mime_type: str
    data: Dict[str, str]


class PresentationRequestMessage(BaseModel):
    id: str
    type: str = (
        "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/request-presentation"
    )
    request: PresentationAttachment
    comment: str
    service: ServiceDecorator


@router.post(VerifiedCredentialAuthorizeUri, response_model=dict)
async def post_authorize(request: Request):
    """Called by oidc platform."""
    logger.debug(f">>> post_authorize")
    logger.debug(f"payload ={request}")

    return {}


@router.get(VerifiedCredentialAuthorizeUri, response_class=HTMLResponse)
async def get_authorize(request: Request):
    """Called by oidc platform."""
    logger.info(f">>> get_authorize")
    model = AuthorizationRequest().from_dict(request.query_params._dict)
    logger.info(model.verify())

    pres_req_conf_id = model.get("pres_req_conf_id")
    logger.info(f"pres_req_conf_id={pres_req_conf_id}")

    if pres_req_conf_id != "test-pres-req":
        raise Exception("pres_req_conf_id not found")

    client = AcapyClient()
    presentation_request = client.create_presentation_request()

    # TODO RETURN WEBPAGE FOR USER TO SCAN
    return f"""
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
            <h3>{model.get("pres_req_conf_id")}</h3>
            <p>{presentation_request}</p>
        </body>
    </html>
    """


#


@router.post(AuthorizeCallbackUri, response_model=dict)
async def get_authorize_callback(request: Request):
    """Called by oidc platform."""
    logger.debug(f">>> get_authorize_callback")
    logger.debug(f"payload ={request}")
    return {}


#


@router.post(VerifiedCredentialTokenUri, response_model=dict)
async def post_token(request: Request):
    """Called by oidc platform."""
    logger.debug(f">>> post_token")
    model = AccessTokenRequest().from_dict(request.query_params._dict)
    logger.info(f"payload ={model}")

    return {}
