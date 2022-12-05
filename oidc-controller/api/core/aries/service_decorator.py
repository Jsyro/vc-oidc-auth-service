from typing import List
from pydantic import BaseModel


class ServiceDecorator(BaseModel):
    # https://github.com/hyperledger/aries-rfcs/tree/main/features/0056-service-decorator
    recipient_keys: List[str]
    routing_keys: List[str]
    service_endpoint: str
