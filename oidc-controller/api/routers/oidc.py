import logging
from typing import List, Dict

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from oic.oic.message import (
    AuthorizationRequest,
    AccessTokenRequest,
)

from oic.utils.jwt import JWT

from oic.oic.message import AccessTokenResponse, IdToken, AuthnToken
from ..core.acapy import AcapyClient
from ..core.aries import PresentationRequestMessage, ServiceDecorator

from ..db.models import AuthSession

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
async def get_authorize(request: Request, state: str):
    """Called by oidc platform."""
    logger.info(f">>> get_authorize")
    model = AuthorizationRequest().from_dict(request.query_params._dict)
    logger.info(model.verify())

    pres_req_conf_id = model.get("pres_req_conf_id")
    logger.info(f"pres_req_conf_id={pres_req_conf_id}")

    if pres_req_conf_id != "test-request-config":
        raise Exception("pres_req_conf_id not found")

    client = AcapyClient()
    response = client.create_presentation_request()
    # TODO RETURN WEBPAGE FOR USER TO SCAN
    msg = PresentationRequestMessage(id=response["presentation_exchange_id"])

    return f"""
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>AUTHORIZATION REQUEST</h1>
            <p>request</p>
            <p>{request.query_params._dict}</p>

            <p>presentation_request</p>
            <p>{response}</p>

            <p> User waits on this screen until Proof has been presented to the vcauth service agent, then is redirected to</p>
            <a href="http://localhost:5201{AuthorizeCallbackUri}?pid={msg.id}&kc_state={state}">callback url (redirect to kc)</a>
        </body>
    </html>
    """


@router.get(AuthorizeCallbackUri, response_class=HTMLResponse)
async def get_authorize_callback(
    request: Request,
    pid: str,
    kc_state: str,
):
    """Called by oidc platform."""
    logger.debug(f">>> get_authorize_callback")
    logger.debug(f"payload ={request}")
    # return {"url": oidc_redirect + "?state=" + kc_state}
    # url = $"{session.RequestParameters[IdentityConstants.RedirectUriParameterName]}?code={session.Id}";
    redirect_uri = "http://localhost:8880/auth/realms/vc-authn/broker/vc-authn/endpoint"
    session_id = pid
    state = kc_state

    url = redirect_uri + "?code=" + session_id + "&state=" + state
    print(url)
    return f"""
    <html>
        <head>
            <title>resulting redirect</title>
        </head>
        <body>
            <a href="{url}">{url}</a>
        </body>
    </html>
    """


@router.post(VerifiedCredentialTokenUri)
async def post_token(request: Request):
    """Called by oidc platform."""
    logger.info(f">>> post_token")
    form = await request.form()
    # logger.info(f"payload ={form}")
    model = AccessTokenRequest().from_dict(form._dict)
    logger.info(f"model ={model}")

    idtoken_payload = {
        "sub": "1af58203-33fa-42a6-8628-a85472a9967e",
        "t_id": "132465e4-c57f-459f-8534-e30e78484f24",
        "exp": 1970305472,
        "nonce": "Slmn277VX-dZ05L44ew1ww",
        "aud": "keycloak",
    }

    # TODO FIND OIC CLASS THAT WILL MAKE ME THIS.
    id_token = IdToken().from_dict(idtoken_payload)
    id_token_jwt = id_token.to_jwt()

    values = {
        "token_type": "bearer",
        "id_token": id_token_jwt,
        "access_token": "invalid",
        "aud": "keycloak",
    }

    response = AccessTokenResponse().from_dict(values)
    return response


@router.post("/vc/connect/{pid}/complete")
async def debug_complete_pid(pid: str):
    logger.debug(">>> debug_complete_pid")
    logger.debug(f"completing presentation_id ={pid}")
    # go back to redirect_url provided by the user

    pass


"""
http://localhost:5201/vc/connect/authorize
?scope=openid+vc_authn
&state=_hvuRgN3Y5fQ5CXcVNCCdHGb0Th3oRgzBFW0vARteQI.2ulcZG7w9GE.vue-fe
&response_type=code
&client_id=keycloak
&redirect_uri=http://localhost:8880/auth/realms/vc-authn/broker/vc-authn/endpoint
&pres_req_conf_id=test-request-config
&nonce=toBFYquhVRQPeKCCi9NtKw
"""

idtoken = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxYWY1ODIwMy0zM2ZhLTQyYTYtODYyOC1hODU0NzJhOTk2N2UiLCJrZXkiOiJleUowZVhBaU9pSktWMVFpTENKaGJHY2lPaUpJVXpJMU5pSjkuZXlKM1lXeHNaWFJmYVdRaU9pSXhZV1kxT0RJd015MHpNMlpoTFRReVlUWXRPRFl5T0MxaE9EVTBOekpoT1RrMk4yVWlMQ0pwWVhRaU9qRTJOekF5T0RjME56SXNJbVY0Y0NJNk1UWTNNRE0zTXpnM01uMC5NbmNFeVpNdE9wOVJYM3NOb3k2SDhrNmszVU44ckg3WXBObm81TV9KNkpVIiwidF9pZCI6IjEzMjQ2NWU0LWM1N2YtNDU5Zi04NTM0LWUzMGU3ODQ4NGYyNCIsImV4cCI6MTY3MDMwNTQ3Mn0.TGzC6istfsKeeJR6Yp0kYTo-WMsOM66sKYSO1OUi3Ug",
)


idtoken_payload = {
    "sub": "1af58203-33fa-42a6-8628-a85472a9967e",
    "t_id": "132465e4-c57f-459f-8534-e30e78484f24",
    "exp": 1670305472,
}

idtoken_payload_key_payload = {
    "wallet_id": "1af58203-33fa-42a6-8628-a85472a9967e",
    "iat": 1670287472,
    "exp": 1670373872,
}
