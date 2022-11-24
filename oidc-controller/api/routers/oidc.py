import logging

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Security

ChallengePollUri = "/vc/connect/poll"
AuthorizeCallbackUri = "/vc/connect/callback"
VerifiedCredentialAuthorizeUri = "/vc/connect/authorize"
VerifiedCredentialTokenUri = "/vc/connect/token"

logger = logging.getLogger(__name__)

router = APIRouter()

#

@router.post(VerifiedCredentialAuthorizeUri, response_model=dict)
async def post_authorize():
    """Called by oidc platform."""
    logger.debug(f">>> post_authorize")
    return {}



@router.get(VerifiedCredentialAuthorizeUri, response_model=dict)
async def get_authorize():
    """Called by oidc platform."""
    logger.debug(f">>> get_authorize")
    return {}

# 

@router.post(AuthorizeCallbackUri, response_model=dict)
async def get_authorize_callback():
    """Called by oidc platform."""
    logger.debug(f">>> get_authorize_callback")
    return {}

#

@router.post(VerifiedCredentialTokenUri, response_model=dict)
async def post_token():
    """Called by oidc platform."""
    logger.debug(f">>> post_token")
    return {}

