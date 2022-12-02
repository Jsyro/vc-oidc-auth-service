import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..core.acapy import AcapyClient

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/dev_create_tenant", response_model=dict)
async def get_access_token(request: Request):
    client = AcapyClient()

    return {"success": client.get_access_token()}
