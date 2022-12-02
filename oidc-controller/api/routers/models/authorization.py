from pydantic import BaseModel


class AuthorizationEndpointModel(BaseModel):
    challenge: str
    pollUrl: str
    resolution_url: str
    interval: int

    presentation_request: str
