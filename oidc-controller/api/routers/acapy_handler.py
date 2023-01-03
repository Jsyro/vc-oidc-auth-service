import logging, json
from typing import List, Dict

from fastapi import APIRouter, Request

from ..db.models import AuthSession
from ..core.acapy.client import AcapyClient

logger = logging.getLogger(__name__)

router = APIRouter()


# @router.post("/{apiKey}/topic/{topic}")
# async def post_topic_with_api_key(request: Request):
#     """Called by oidc platform."""
#     logger.debug(f">>> post_topic_with_api_key")
#     logger.debug(f"payload ={request}")

#     return {}


async def _parse_webhook_body(request: Request):
    return json.loads((await request.body()).decode("ascii"))


@router.post("/topic/{topic}/")
async def post_topic(request: Request, topic: str):
    """Called by oidc platform."""
    logger.info(f">>> post_topic : topic={topic}")
    client = AcapyClient()
    match topic:
        case "present_proof":
            webhook_body = await _parse_webhook_body(request)
            logger.info(webhook_body)
            session: AuthSession = await AuthSession.find_by_pres_req_id(
                webhook_body["presentation_exchange_id"]
            )
            if webhook_body["state"] == "presentation_received":

                logger.info("GOT A RESPONSE, TIME TO VERIFY")
                resp = client.verify_presentation(session.presentation_request_id)
                logger.info(resp)
            if webhook_body["state"] == "verified":
                logger.info("VERIFIED")
                session.presentation_request_satisfied = True
                # update presentation_exchange record
                session.presentation_request = webhook_body

                await session.save()

            pass
        case other:
            logger.debug("skipping webhook")

    return {}
