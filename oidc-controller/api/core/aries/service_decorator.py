from typing import List, Optional
from pydantic import BaseModel


class ServiceDecorator(BaseModel):
    # https://github.com/hyperledger/aries-rfcs/tree/main/features/0056-service-decorator
    recipient_keys: Optional[List[str]]
    routing_keys: Optional[List[str]]
    service_endpoint: Optional[str]
