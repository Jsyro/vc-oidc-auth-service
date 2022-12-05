from pydantic import BaseModel
from . import PresentProofv10Attachment, ServiceDecorator


class PresentationRequestMessage(BaseModel):
    # https://github.com/hyperledger/aries-rfcs/blob/main/features/0037-present-proof/README.md#presentation
    id: str
    type: str = (
        "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/request-presentation"
    )
    request: PresentProofv10Attachment
    comment: str
    service: ServiceDecorator
