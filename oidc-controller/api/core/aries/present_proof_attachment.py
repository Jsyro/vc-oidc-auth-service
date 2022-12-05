from typing import Dict
from pydantic import BaseModel


class PresentProofv10Attachment(BaseModel):
    # https://github.com/hyperledger/aries-rfcs/blob/main/features/0037-present-proof/README.md#request-presentation
    id: str
    mime_type: str
    data: Dict[str, str]
