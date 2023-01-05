import logging, json, base64, io

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from oic.oic.message import (
    AuthorizationRequest,
    AccessTokenRequest,
    AccessTokenResponse,
    IdToken,
)
import qrcode

from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import get_async_session


from ..core.acapy.client import AcapyClient
from ..core.oidc.issue_token_service import Token
from ..db.models import AuthSession
from ..verificationConfigs.crud import VerificationConfigCRUD

ChallengePollUri = "/poll"
AuthorizeCallbackUri = "/callback"
VerifiedCredentialAuthorizeUri = "/authorize"
VerifiedCredentialTokenUri = "/token"

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(VerifiedCredentialAuthorizeUri, response_model=dict)
async def post_authorize(request: Request):
    """Called by oidc platform."""
    logger.debug(f">>> post_authorize")
    logger.debug(f"payload ={request}")

    return {}


@router.get(VerifiedCredentialAuthorizeUri, response_class=HTMLResponse)
async def get_authorize(
    request: Request,
    state: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Called by oidc platform."""
    logger.debug(f">>> get_authorize")

    # Verify OIDC forward payload
    model = AuthorizationRequest().from_dict(request.query_params._dict)
    model.verify()

    client = AcapyClient()
    pres_req_conf_id = model.get("pres_req_conf_id")

    ver_configs = VerificationConfigCRUD(session)
    ver_config = await ver_configs.get(pres_req_conf_id)
    logger.warn(ver_config)
    if not ver_config:
        raise HTTPException(status=404, detail="pres_req_conf_id not found")

    # Create presentation_request to show on screen
    response = client.create_presentation_request(ver_config.generate_proof_request())

    # save OIDC AuthSession
    session = AuthSession(
        request_parameters=model.to_dict(),
        presentation_record_id=pres_req_conf_id,
        presentation_request_id=response.presentation_exchange_id,
        presentation_request=response,
    )
    await session.save()

    # QR CONTENTS
    controller_host = "https://0385-165-225-211-70.ngrok.io"
    url_to_message = (
        controller_host + "/url/pres_req/" + str(session.presentation_request_id)
    )

    # CREATE an image?
    buff = io.BytesIO()
    qrcode.make(url_to_message).save(buff, format="PNG")
    image_contents = base64.b64encode(buff.getvalue()).decode("utf-8")

    return f"""
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>AUTHORIZATION REQUEST</h1>

            <p>Scan this QR code for a connectionless present-proof request</p>
            <p><img src="data:image/jpeg;base64,{image_contents}" alt="{image_contents}" width="300px" height="300px" /></p>

            <p> User waits on this screen until Proof has been presented to the vcauth service agent, then is redirected to</p>
            <a href="http://localhost:5201/vc/connect{AuthorizeCallbackUri}?pid={session.id}">callback url (redirect to kc)</a>
        </body>
    </html>
    """


@router.get(AuthorizeCallbackUri, response_class=HTMLResponse)
async def get_authorize_callback(
    request: Request,
    pid: str,
):
    """Called by oidc platform."""
    logger.debug(f">>> get_authorize_callback")
    logger.debug(f"payload ={request}")
    # return {"url": oidc_redirect + "?state=" + kc_state}
    # url = $"{session.RequestParameters[IdentityConstants.RedirectUriParameterName]}?code={session.Id}";
    redirect_uri = "http://localhost:8880/auth/realms/vc-authn/broker/vc-authn/endpoint"
    session = await AuthSession.find_by_id(pid)

    url = (
        redirect_uri
        + "?code="
        + str(session.id)
        + "&state="
        + str(session.request_parameters["state"])
    )
    print(url)
    return f"""
    <html>
        <head>
            <title>Resulting redirect</title>
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
    session: AuthSession = await AuthSession.find_by_id(model.get("code"))
    client = AcapyClient()

    # RETURNS HARDCODED PRESENTATION WITH VERIFIED PROOF
    presentation = client.get_presentation_request(session.presentation_request_id)

    claims = Token.get_claims(presentation, session)
    claims = {c.type: c for c in claims}

    token = Token(
        issuer="placeholder", audiences=["keycloak"], lifetime=10000, claims=claims
    )

    idtoken_payload = {
        "sub": "1af58203-33fa-42a6-8628-a85472a9967e",
        "t_id": "132465e4-c57f-459f-8534-e30e78484f24",
        "exp": 1970305472,
        "nonce": session.request_parameters["nonce"],
        "aud": "keycloak",
    }
    logger.warn("WORKING EXAMPLE:")
    logger.warn(IdToken().from_dict(idtoken_payload))
    id_token = IdToken().from_dict(
        token.idtoken_dict(session.request_parameters["nonce"])
    )
    logger.warn(session.request_parameters["nonce"])
    logger.info(id_token)
    id_token_jwt = id_token.to_jwt()
    logger.info(id_token_jwt)

    values = {
        "token_type": "bearer",
        "id_token": id_token_jwt,
        "access_token": "invalid",
        "aud": "keycloak",
    }

    response = AccessTokenResponse().from_dict(values)
    logger.info(response)
    return response


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
