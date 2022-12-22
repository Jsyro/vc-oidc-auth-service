import logging, json, base64, io
from typing import List, Dict
from base64 import encodebytes
from PIL import Image

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from ..core.url_shorten_service import resolve_url

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/url/{pid}")
async def get_url(
    request: Request,
    pid: str,
):
    return JSONResponse(
        {
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
                "serviceEndpoint": "https://80aa-165-225-211-70.ngrok.io",
            },
        }
    )
    # logger.warning(request.headers)
    # url = await resolve_url(pid)
    # if not url:
    #     raise HTTPException(status_code=404)

    # return RedirectResponse(url, 302)
