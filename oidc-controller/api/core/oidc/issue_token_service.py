import logging
from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel

from oic.oic.message import IdToken
from oic.utils.jwt import JWT

from ...authSessions.models import AuthSession

logger = logging.getLogger(__name__)


class Claim(BaseModel):
    type: str
    value: str

    # vc-authn-oidc uses this class/constructor
    # https://learn.microsoft.com/en-us/dotnet/api/system.security.claims.claim.-ctor?view=net-7.0#system-security-claims-claim-ctor(system-string-system-string)


class Token(BaseModel):
    creation_time: datetime = datetime.now()
    issuer: str
    audiences: List[str]
    lifetime: int
    claims: Dict[str, Claim]

    @classmethod
    def get_claims(cls, pres_exch: Dict, auth_session: AuthSession) -> List["Claim"]:
        logger.debug(f">>> Token.get_claims")
        logger.info(pres_exch)

        claims: List[Claim] = [
            Claim(
                type="pres_req_conf_id",
                value=auth_session.request_parameters["pres_req_conf_id"],
            ),
            Claim(type="acr", value="vc_authn"),
        ]

        # subject claim
        claims.append(Claim(type="sub", value="FROM_PROOF_REQUEST"))
        claims.append(
            Claim(type="nonce", value=auth_session.request_parameters["nonce"])
        )

        for requested_attr in auth_session.presentation_exchange[
            "presentation_request"
        ]["requested_attributes"].values():

            # loop through each value and put it in token as a claim
            revealed_attrs: Dict = auth_session.presentation_exchange["presentation"][
                "requested_proof"
            ]["revealed_attrs"]
            for k, v in revealed_attrs.items():
                claims.append(Claim(type=requested_attr["name"], value=v["raw"]))
            return claims

    def idtoken_dict(self, nonce: str) -> Dict:
        result = {}
        for claim in self.claims.values():
            result[claim.type] = claim.value

        result["sub"] = "1af58203-33fa-42a6-8628-a85472a9967e"
        result["t_id"] = "132465e4-c57f-459f-8534-e30e78484f24"
        result["exp"] = int(round(datetime.now().timestamp())) + self.lifetime
        result["aud"] = self.audiences
        result["nonce"] = nonce

        return result


class IssueTokenService:
    def issue_token(claims):
        token = Token(
            issuer="issuer",
            audiences=["keycloak"],
            lifetime=10000,
        )

    pass
