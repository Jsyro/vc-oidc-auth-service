import logging, json
from typing import List, Dict

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
async def post_pres_req_conf(request: Request):
    pass

@router.get("/")
async def get_pres_req_conf(request: Request):
    pass


@router.delete("/")
async def del_pres_req_conf(request: Request):
    pass


@router.put("/")
async def put_pres_req_conf(request: Request):
    pass