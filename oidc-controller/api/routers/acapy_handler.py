import logging
from typing import List, Dict

from fastapi import APIRouter, Request


logger = logging.getLogger(__name__)

router = APIRouter()



@router.post("/{apiKey}/topic/{topic}")
async def post_topic_with_api_key(request: Request):
    """Called by oidc platform."""
    logger.debug(f">>> post_topic_with_api_key")
    logger.debug(f"payload ={request}")

    return {}



@router.post("/topic/{topic}")
async def post_topic(request: Request):
    """Called by oidc platform."""
    logger.debug(f">>> post_topic")
    logger.debug(f"payload ={request}")

    return {}
