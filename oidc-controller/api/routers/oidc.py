import logging, json, base64
from typing import List, Dict
from base64 import encodebytes

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from oic.oic.message import (
    AuthorizationRequest,
    AccessTokenRequest,
     AccessTokenResponse, IdToken
)

from oic.utils.jwt import JWT

from ..core.acapy.client import AcapyClient
from ..core.aries import PresentationRequestMessage, ServiceDecorator, PresentProofv10Attachment

from ..db.models import AuthSession, PresentationConfiguration

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
async def get_authorize(request: Request, state: str):
    """Called by oidc platform."""
    logger.debug(f">>> get_authorize")


    req_dict = {
            "auto_verify": False,
            "comment": "string",
            "proof_request": {
                "name": "Proof request",
                "requested_attributes": {
                    "prop1": {
                        "name": "first_name",
                        "non_revoked": {},
                        "restrictions": [],
                    },
                    "prop2": {
                        "name": "last_name",
                        "non_revoked": {},
                        "restrictions": [],
                    },
                },
                "requested_predicates": {},
                "non_revoked": {},
            },
            "name": "test_pres_conf",
            "version": "1.0.0",
        }
    # Verify OIDC forward payload
    model = AuthorizationRequest().from_dict(request.query_params._dict)
    model.verify()

    # Load pres_req_conf_id
    pres_req_conf_id = model.get("pres_req_conf_id")
    pres_config = await PresentationConfiguration.find_by_pres_req_conf_id(pres_req_conf_id)
    pres_req = pres_config.presentation_request_configuration if pres_config else req_dict

    # Create presentation_request to show on screen
    client = AcapyClient()
    response = client.create_presentation_request(pres_req)

    #build payload
    attachment = PresentProofv10Attachment(data={"base64":base64.b64encode(json.dumps(response["presentation_request"]).encode("utf-8"))})

    #register and save public did
    public_did = client.get_wallet_public_did().result
    service_endpoint = "https://26ab-165-225-211-70.ngrok.io" #from ngrok
   

    s_d = ServiceDecorator(service_endpoint=service_endpoint, recipient_keys=[public_did.verkey])
    #bundle everything needed for the QR code
    msg = PresentationRequestMessage(id=response["presentation_exchange_id"], request=attachment, service=s_d)

    #save OIDC AuthSession
    session = AuthSession(
        request_parameters=model.to_dict(),
        presentation_record_id=pres_req_conf_id,
        presentation_request_id=response["presentation_exchange_id"],
        presentation_request=response,
    )
    await session.save()


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
            <a href="http://localhost:5201/vc/connect{AuthorizeCallbackUri}?pid={session.id}">callback url (redirect to kc)</a>

            <p> Packaged with the appropriate aries requirement</p>
            <p>{msg.dict()}</p>



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

    url = redirect_uri + "?code=" + str(session.id) + "&state="+ str(session.request_parameters["state"])
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
    session = await AuthSession.find_by_id(model.get("code"))
    
    idtoken_payload = {
        "sub": "1af58203-33fa-42a6-8628-a85472a9967e",
        "t_id": "132465e4-c57f-459f-8534-e30e78484f24",
        "exp": 1970305472,
        "nonce": session.request_parameters["nonce"],
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
