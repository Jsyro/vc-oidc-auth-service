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
from ..core.acapy import AcapyClient
from ..core.aries import PresentationRequestMessage

ChallengePollUri = "/vc/connect/poll"
AuthorizeCallbackUri = "/vc/connect/callback"
VerifiedCredentialAuthorizeUri = "/vc/connect/authorize"
VerifiedCredentialTokenUri = "/vc/connect/token"

logger = logging.getLogger(__name__)

router = APIRouter()


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

    if pres_req_conf_id != "test-request-config":
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
            <a href={model.get("redirect_url")}>redirect to app</a>
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


@router.post("/vc/connect/{pid}/complete")
async def debug_complete_pid(pid: str):
    logger.debug(">>> debug_complete_pid")
    logger.debug(f"completing presentation_id ={pid}")
    # go back to redirect_url provided by the user

    pass
