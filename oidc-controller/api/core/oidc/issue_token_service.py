import logging
from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel

from oic.oic.message import IdToken
from oic.utils.jwt import JWT

from ...db.models import AuthSession

logger = logging.getLogger(__name__)


class Claim(BaseModel):
    # issuer: str
    type: str  # sub, nonce, iss, iat, acr
    value: str
    # value_type: str

    # vc-authn-oidc uses this class/constructor
    # https://learn.microsoft.com/en-us/dotnet/api/system.security.claims.claim.-ctor?view=net-7.0#system-security-claims-claim-ctor(system-string-system-string)

    pass


class Token(BaseModel):
    creation_time: datetime = datetime.now()
    issuer: str
    audiences: List[str]
    lifetime: int
    claims: Dict[str, Claim]

    def __init__(self, *, issuer: str, audiences: List[str], lifetime: int, claims):
        self.issuer = issuer
        self.audiences = audiences
        self.lifetime = lifetime
        self.claims = claims

    def get_claims(pres_exch: Dict, auth_session: AuthSession):
        logger.debug(f">>> Token.get_claims")
        logger.info(pres_exch)

        claims: List[Claim] = [
            Claim(type="pres_req_conf_id", value=pres_exch["presentation_exchange_id"]),
            Claim(type="acr", value="vc_authn"),
        ]

        # subject claim
        claims.append(Claim(type="sub", value="FROM_PROOF_REQUEST"))
        claims.append(
            Claim(type="nonce", value=auth_session.request_parameters["nonce"])
        )

        # loop through each value and put it in token as a claim

        return claims


class IssueTokenService:
    def issue_token(claims):
        token = Token(
            issuer="issuer",
            audiences=["keycloak"],
            lifetime=10000,
        )

    pass
