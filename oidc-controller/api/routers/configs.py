import logging, json
from typing import List, Dict

from fastapi import APIRouter, Request, HTTPException

from ..db.models import PresentationConfiguration
from ..db.session import db


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
async def post_pres_req_conf(request: Request):
    pres = PresentationConfiguration()
    pres.save()
    pass


@router.get("/{pres_req_conf_id}")
async def get_pres_req_conf(request: Request, pres_req_conf_id: str):
    pres = await PresentationConfiguration.find_by_pres_req_conf_id(pres_req_conf_id)
    if not pres:
        raise HTTPException(
            status_code=404, detail="PresentationConfiguration not found"
        )

    return pres


@router.delete("/{pres_req_conf_id}")
async def del_pres_req_conf(request: Request, pres_req_conf_id: str):
    pres = await PresentationConfiguration.find_by_pres_req_conf_id(pres_req_conf_id)
    if not pres:
        raise HTTPException(
            status_code=404, detail="PresentationConfiguration not found"
        )
    pres.delete()

    pass


@router.put("/{pres_req_conf_id}")
async def put_pres_req_conf(request: Request, pres_req_conf_id: str):
    pres = await PresentationConfiguration.find_by_pres_req_conf_id(pres_req_conf_id)
    if not pres:
        raise HTTPException(
            status_code=404, detail="PresentationConfiguration not found"
        )

    # pres.update()
    return pres
