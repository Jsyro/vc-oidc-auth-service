import logging

from fastapi import APIRouter, Request


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/trigger/", response_model=dict)
async def get_access_token(request: Request):
    pass
    # return {"success": }
