import json
from typing import Dict
from pydantic import BaseModel


class PresentProofv10Attachment(BaseModel):
    # https://github.com/hyperledger/aries-rfcs/blob/main/features/0037-present-proof/README.md#request-presentation
    id: str ="libindy-request-presentation-0"
    mime_type: str = "application/json"
    data: Dict
       