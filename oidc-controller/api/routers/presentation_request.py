import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

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
async def send_connectionless_proof_req(
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
    msg = PresentationRequestMessage(
        id=auth_session.presentation_request["thread_id"],
        request=[byo_attachment],
        service=s_d,
    )

    return JSONResponse(msg.dict(by_alias=True))
