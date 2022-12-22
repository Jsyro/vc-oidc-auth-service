import logging, json, base64, io
from typing import List, Dict
from base64 import encodebytes
from PIL import Image

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from ..db.models import AuthSession
from ..core.acapy.client import AcapyClient

from ..core.aries import (
    PresentationRequestMessage,
    ServiceDecorator,
    PresentProofv10Attachment,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/url/pres_req/{pres_req_id}")
async def get_url(
    request: Request,
    pres_req_id: str,
):
    auth_session: AuthSession = await AuthSession.find_by_pres_req_id(pres_req_id)
    client = AcapyClient()

    public_did = client.get_wallet_public_did()

    s_d = ServiceDecorator(
        service_endpoint=client.service_endpoint, recipient_keys=[public_did.verkey]
    )

    # bundle everything needed for the QR code
    byo_attachment = PresentProofv10Attachment.build(
        auth_session.presentation_request["presentation_request"]
    )
    logger.info(auth_session.presentation_request["presentation_request"])
    # logger.info(byo_attachment)
    msg = PresentationRequestMessage(
        id=auth_session.presentation_request["thread_id"],
        request=[byo_attachment],
        service=s_d,
    )

    msg_dict = msg.request[0].dict(by_alias=True)

    known_dict = {
        "@id": "2030894a-41a8-4eb5-bb6b-206371c37a75",
        "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/request-presentation",
        "request_presentations~attach": [
            {
                "@id": "libindy-request-presentation-0",
                "mime-type": "application/json",
                "data": {
                    "base64": "eyJub25jZSI6ICI2MDE3MDcyMzg1NjQ1MzM2NDkxNTY2MzYiLCAibmFtZSI6ICJQcm9vZnJlcXVlc3QiLCAidmVyc2lvbiI6ICIwLjEuMCIsICJyZXF1ZXN0ZWRfYXR0cmlidXRlcyI6IHsicHJvcDEiOiB7Im5hbWUiOiAiZmlyc3RfbmFtZSIsICJyZXN0cmljdGlvbnMiOiBbXX0sICJwcm9wMiI6IHsibmFtZSI6ICJsYXN0X25hbWUiLCAicmVzdHJpY3Rpb25zIjogW119fSwgInJlcXVlc3RlZF9wcmVkaWNhdGVzIjoge319"
                },
            }
        ],
        "comment": None,
        "~service": {
            "recipientKeys": ["HqnSR3Nic6R8X6S9LVC21yvDq4okqBQne6LLCbrqT9Rj"],
            "routingKeys": None,
            "serviceEndpoint": "https://2b8d-165-225-211-70.ngrok.io",
        },
    }
    logger.info("msg_dict")
    logger.info(msg_dict)
    logger.info("known_dict")
    logger.info(known_dict)

    # return JSONResponse(msg.dict(by_alias=True))
    return JSONResponse(known_dict)
