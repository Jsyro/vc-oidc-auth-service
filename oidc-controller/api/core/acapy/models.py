from typing import Optional

from pydantic import BaseModel

class WalletPublicDid(BaseModel):
    did:str
    verkey:str
    public:bool

class WalletDidPublicResponse(BaseModel):
    result: Optional[WalletPublicDid]
