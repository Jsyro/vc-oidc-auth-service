import logging, json, base64, io
from typing import List, Dict
from base64 import encodebytes
from PIL import Image

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from oic.oic.message import (
    AuthorizationRequest,
    AccessTokenRequest,
    AccessTokenResponse,
    IdToken,
)
import qrcode

from ..core.acapy.client import AcapyClient
from ..core.aries import (
    PresentationRequestMessage,
    ServiceDecorator,
    PresentProofv10Attachment,
)
from ..core.oidc.issue_token_service import Token
from ..core.url_shorten_service import create_url
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
    logger.warning(request.headers)
    req_dict = {
        "auto_verify": False,
        "comment": "AWDAWD",
        "proof_request": {
            "name": "Proofrequest",
            "version": "0.1.0",
            "requested_attributes": {
                "prop1": {
                    "name": "first_name",
                    "restrictions": [],
                },
                "prop2": {
                    "name": "last_name",
                    "restrictions": [],
                },
            },
            "requested_predicates": {},
        },
    }

    # Verify OIDC forward payload
    model = AuthorizationRequest().from_dict(request.query_params._dict)
    model.verify()

    client = AcapyClient()

    service_endpoint = client.service_endpoint

    # Load pres_req_conf_id
    pres_req_conf_id = model.get("pres_req_conf_id")
    pres_config = await PresentationConfiguration.find_by_pres_req_conf_id(
        pres_req_conf_id
    )
    pres_req = (
        pres_config.presentation_request_configuration if pres_config else req_dict
    )

    # Create presentation_request to show on screen
    response = client.create_presentation_request(pres_req)
    # logger.info(response)

    public_did = client.get_wallet_public_did()

    s_d = ServiceDecorator(
        service_endpoint=service_endpoint, recipient_keys=[public_did.verkey]
    )

    # build payload

    # build message like acapy demo.
    logger.info(response.presentation_exchange_id)
    response2 = client.get_presentation_request(response.presentation_exchange_id)
    pres_exch_txn = response2["presentation_request_dict"]
    pres_exch_txn["~service"] = s_d.dict()
    obj_json_str = json.dumps(pres_exch_txn)
    obj_json_b64 = base64.urlsafe_b64encode(obj_json_str.encode("ascii"))
    qr_content_acapy_test_style = (
        service_endpoint + "?m=" + obj_json_b64.decode("ascii")
    )
    logger.info("qr_content_acapy_test_style")
    # logger.info(qr_content_acapy_test_style)

    # register and save public did
    known_good_attachment = PresentProofv10Attachment(
        data={
            "base64": "eyJuYW1lIjoiY2l0ei12ZXJpZmllZC1wZXJzb24iLCJuYW1lcyI6bnVsbCwidmVyc2lvbiI6IjAuMS4wIiwibm9uY2UiOiI5MDA2ODgwODE5NTcwMDcyMTQ5Mjc2ODAiLCJyZXF1ZXN0ZWRfYXR0cmlidXRlcyI6eyIzNjYxZTg5Yi02NTRkLTQ2OTUtODczZC0zMjMxNjRiZTQyZWIiOnsibmFtZXMiOlsiZ2l2ZW5OYW1lIiwiYWRkaXRpb25hbE5hbWUiLCJmYW1pbHlOYW1lIiwiZGF0ZU9mQmlydGgiLCJzdHJlZXRBZGRyZXNzIiwicG9zdGFsQ29kZSIsImxvY2FsaXR5IiwicmVnaW9uIiwiY291bnRyeSIsInBob25lTnVtYmVyIiwiYWx0ZXJuYXRlUGhvbmVOdW1iZXIiLCJlbWFpbCIsImdlbmRlciIsImlzc3VlciIsImlzc3VlRGF0ZSIsImV4cGlyYXRpb25EYXRlIiwiSWRlbnRpdHlMZXZlbE9mQXNzdXJhbmNlIl0sInJlc3RyaWN0aW9ucyI6W3sic2NoZW1hX2lzc3Vlcl9kaWQiOiI2NkFnTDlOSms4cDliQnB6WG1YS2Q5Iiwic2NoZW1hX25hbWUiOiJ2ZXJpZmllZF9wZXJzb24iLCJzY2hlbWFfdmVyc2lvbiI6IjAuMS4yIn1dfX0sInJlcXVlc3RlZF9wcmVkaWNhdGVzIjp7fX0="
        }
    )
    # bundle everything needed for the QR code
    byo_attachment = PresentProofv10Attachment.build(response.presentation_request)

    msg = PresentationRequestMessage(
        id=response.thread_id,
        request=[byo_attachment],
        service=s_d,
    )
    logger.warning(msg.dict(by_alias=True))
    # save OIDC AuthSession
    session = AuthSession(
        request_parameters=model.to_dict(),
        presentation_record_id=pres_req_conf_id,
        presentation_request_id=response.presentation_exchange_id,
        presentation_request=response,
    )
    await session.save()

    # QR CONTENTS
    qr_content = service_endpoint + "?m=" + msg.b64_str()
    logger.info("qr_content_vcauthn_style")
    # logger.info(qr_content)

    KNOWN_WORKING_QR_HOST = (
        "https://toip-vc-authn-controller-test.apps.silver.devops.gov.bc.ca/?m="
    )
    KNOWN_WORKING_QR = "eyJAaWQiOiJlNjZhYmE5My1mZDhjLTQwNmUtYjYzZi1jZGI0NDQ5NGNkZjUiLCJAdHlwZSI6ImRpZDpzb3Y6QnpDYnNOWWhNcmpIaXFaRFRVQVNIZztzcGVjL3ByZXNlbnQtcHJvb2YvMS4wL3JlcXVlc3QtcHJlc2VudGF0aW9uIiwicmVxdWVzdF9wcmVzZW50YXRpb25zfmF0dGFjaCI6W3siQGlkIjoibGliaW5keS1yZXF1ZXN0LXByZXNlbnRhdGlvbi0wIiwibWltZS10eXBlIjoiYXBwbGljYXRpb24vanNvbiIsImRhdGEiOnsiYmFzZTY0IjoiZXlKdVlXMWxJam9pWTJsMGVpMTJaWEpwWm1sbFpDMXdaWEp6YjI0aUxDSnVZVzFsY3lJNmJuVnNiQ3dpZG1WeWMybHZiaUk2SWpBdU1TNHdJaXdpYm05dVkyVWlPaUl4T1RrNU56SXpOelEwTlRnd056STRNRFF4TlRnek1ETWlMQ0p5WlhGMVpYTjBaV1JmWVhSMGNtbGlkWFJsY3lJNmV5SXdaRFV3TjJVd05TMW1NREl4TFRRd01XSXRZakExWlMwek9URTBaRE5oWlRVeVlqQWlPbnNpYm1GdFpYTWlPbHNpWjJsMlpXNU9ZVzFsSWl3aVlXUmthWFJwYjI1aGJFNWhiV1VpTENKbVlXMXBiSGxPWVcxbElpd2laR0YwWlU5bVFtbHlkR2dpTENKemRISmxaWFJCWkdSeVpYTnpJaXdpY0c5emRHRnNRMjlrWlNJc0lteHZZMkZzYVhSNUlpd2ljbVZuYVc5dUlpd2lZMjkxYm5SeWVTSXNJbkJvYjI1bFRuVnRZbVZ5SWl3aVlXeDBaWEp1WVhSbFVHaHZibVZPZFcxaVpYSWlMQ0psYldGcGJDSXNJbWRsYm1SbGNpSXNJbWx6YzNWbGNpSXNJbWx6YzNWbFJHRjBaU0lzSW1WNGNHbHlZWFJwYjI1RVlYUmxJaXdpU1dSbGJuUnBkSGxNWlhabGJFOW1RWE56ZFhKaGJtTmxJbDBzSW5KbGMzUnlhV04wYVc5dWN5STZXM3NpYzJOb1pXMWhYMmx6YzNWbGNsOWthV1FpT2lJMk5rRm5URGxPU21zNGNEbGlRbkI2V0cxWVMyUTVJaXdpYzJOb1pXMWhYMjVoYldVaU9pSjJaWEpwWm1sbFpGOXdaWEp6YjI0aUxDSnpZMmhsYldGZmRtVnljMmx2YmlJNklqQXVNUzR5SW4xZGZYMHNJbkpsY1hWbGMzUmxaRjl3Y21Wa2FXTmhkR1Z6SWpwN2ZYMD0ifX1dLCJjb21tZW50IjpudWxsLCJ-c2VydmljZSI6eyJyZWNpcGllbnRLZXlzIjpbIkhHZVVURnVaQ00xZjJGdWJWbllHYzF4QWhnQVBFekJGUVJjZnhjcE5qV2JtIl0sInJvdXRpbmdLZXlzIjpudWxsLCJzZXJ2aWNlRW5kcG9pbnQiOiJodHRwczovL3RvaXAtdmMtYXV0aG4tYWdlbnQtdGVzdC5hcHBzLnNpbHZlci5kZXZvcHMuZ292LmJjLmNhIn19"

    vcauthn_message = "https://toip-vc-authn-controller-test.apps.silver.devops.gov.bc.ca?m=eyJAaWQiOiI2MGJhMWU5Ny1jZDA2LTQ5OGQtODQ3Mi1kNDUyOTlhN2I5MzkiLCJAdHlwZSI6ImRpZDpzb3Y6QnpDYnNOWWhNcmpIaXFaRFRVQVNIZztzcGVjL3ByZXNlbnQtcHJvb2YvMS4wL3JlcXVlc3QtcHJlc2VudGF0aW9uIiwicmVxdWVzdF9wcmVzZW50YXRpb25zfmF0dGFjaCI6W3siQGlkIjoibGliaW5keS1yZXF1ZXN0LXByZXNlbnRhdGlvbi0wIiwibWltZS10eXBlIjoiYXBwbGljYXRpb24vanNvbiIsImRhdGEiOnsiYmFzZTY0IjoiZXlKdVlXMWxJam9pWTJsMGVpMTJaWEpwWm1sbFpDMXdaWEp6YjI0aUxDSnVZVzFsY3lJNmJuVnNiQ3dpZG1WeWMybHZiaUk2SWpBdU1TNHdJaXdpYm05dVkyVWlPaUl4TVRjM09EZzFOREF6TWpJM016STBOVFl3TXpFd01UazJJaXdpY21WeGRXVnpkR1ZrWDJGMGRISnBZblYwWlhNaU9uc2lObVV4TXpZMU5UQXRaVEF6TlMwME5UWTRMV0kyWlRVdE1qUmlaR0kxTWpjd01XUTBJanA3SW01aGJXVnpJanBiSW1kcGRtVnVUbUZ0WlNJc0ltRmtaR2wwYVc5dVlXeE9ZVzFsSWl3aVptRnRhV3g1VG1GdFpTSXNJbVJoZEdWUFprSnBjblJvSWl3aWMzUnlaV1YwUVdSa2NtVnpjeUlzSW5CdmMzUmhiRU52WkdVaUxDSnNiMk5oYkdsMGVTSXNJbkpsWjJsdmJpSXNJbU52ZFc1MGNua2lMQ0p3YUc5dVpVNTFiV0psY2lJc0ltRnNkR1Z5Ym1GMFpWQm9iMjVsVG5WdFltVnlJaXdpWlcxaGFXd2lMQ0puWlc1a1pYSWlMQ0pwYzNOMVpYSWlMQ0pwYzNOMVpVUmhkR1VpTENKbGVIQnBjbUYwYVc5dVJHRjBaU0lzSWtsa1pXNTBhWFI1VEdWMlpXeFBaa0Z6YzNWeVlXNWpaU0pkTENKeVpYTjBjbWxqZEdsdmJuTWlPbHQ3SW5OamFHVnRZVjlwYzNOMVpYSmZaR2xrSWpvaU5qWkJaMHc1VGtwck9IQTVZa0p3ZWxodFdFdGtPU0lzSW5OamFHVnRZVjl1WVcxbElqb2lkbVZ5YVdacFpXUmZjR1Z5YzI5dUlpd2ljMk5vWlcxaFgzWmxjbk5wYjI0aU9pSXdMakV1TWlKOVhYMTlMQ0p5WlhGMVpYTjBaV1JmY0hKbFpHbGpZWFJsY3lJNmUzMTkifX1dLCJjb21tZW50IjpudWxsLCJ-c2VydmljZSI6eyJyZWNpcGllbnRLZXlzIjpbIkhHZVVURnVaQ00xZjJGdWJWbllHYzF4QWhnQVBFekJGUVJjZnhjcE5qV2JtIl0sInJvdXRpbmdLZXlzIjpudWxsLCJzZXJ2aWNlRW5kcG9pbnQiOiJodHRwczovL3RvaXAtdmMtYXV0aG4tYWdlbnQtdGVzdC5hcHBzLnNpbHZlci5kZXZvcHMuZ292LmJjLmNhIn19"
    logger.info("vcauthn_message")
    # logger.info(vcauthn_message)

    url = qr_content
    logger.info(url)

    short_url = await create_url(url)

    # CREATE an image?
    buff = io.BytesIO()
    qrcode.make(short_url).save(buff, format="PNG")
    # qrcode.make(qr_content).save(buff, format="PNG")
    image_contents = base64.b64encode(buff.getvalue()).decode("utf-8")

    return f"""
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>AUTHORIZATION REQUEST</h1>
            <p>request to be save as AuthSession</p>
            <p>{request.query_params._dict}</p>

            <p><img src="data:image/jpeg;base64,{image_contents}" alt="{image_contents}" width="600px" height="600px" /></p>
            <p>{short_url}</p>
            <p>{url}</p>


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
    Token(issuer="", audiences=["keycloak"], lifetime=10000, claims=claims)
    # logger.info(presentation)

    idtoken_payload = {
        "sub": "1af58203-33fa-42a6-8628-a85472a9967e",
        "t_id": "132465e4-c57f-459f-8534-e30e78484f24",
        "exp": 1970305472,
        "nonce": session.request_parameters["nonce"],
        "aud": "keycloak",
    }

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
