from datetime import datetime
from typing import List, Dict

from oic.oic.message import IdToken
from oic.utils.jwt import JWT


class Claim:
    pass


class Token:
    creation_time: datetime = datetime.now()
    issuer: str
    audiences: List[str]
    lifetime: int
    claims = Dict[str, Claim]

    def __init__(self, *, issuer: str, audiences: List[str], lifetime: int, claims):
        self.issuer = issuer
        self.audiences = audiences
        self.lifetime = lifetime
        self.claims = claims

    def get_claims():
        pass


class IssueTokenService:
    def issue_token(claims):
        token = Token(
            issuer="issuer",
            audiences=["keycloak"],
            lifetime=10000,
        )

    pass
