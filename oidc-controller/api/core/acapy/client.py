import requests
import json
import logging

from .models import WalletDidPublicResponse, WalletPublicDid

from api.db.models.presentation_request_config import PresentationRequestConfiguration

_client = None
logger = logging.getLogger(__name__)

WALLET_DID_URI = "/wallet/did/public"
CREATE_PRESENTATION_REQUEST_URL = "/present-proof/create-request"


class AcapyClient:
    wallet_id = "8aa25ad7-0686-45e2-87e2-d0f9beb8b983"

    acapy_host = "http://traction-agent:8031"
    acapy_x_api_key = "change-me"

    wallet_token: str = None

    def __init__(self):
        if _client:
            return _client
        super().__init__()

    def get_wallet_token(self):
        logger.info(f">>> get_wallet_token")
        resp_raw = requests.post(
            self.acapy_host + f"/multitenancy/wallet/{self.wallet_id}/token",
            data={"wallet_key": "sample_key"},
            headers={"X-API-KEY": self.acapy_x_api_key},
        )
        assert (
            resp_raw.status_code == 200
        ), f"{resp_raw.status_code}::{resp_raw.content}"
        resp = json.loads(resp_raw.content)
        self.wallet_token = resp["token"]
        return self.wallet_token

    def create_presentation_request(self, presentation_request_configuration: dict):
        if not self.wallet_token:
            self.get_wallet_token()

        logger.debug(f">>> create_presentation_request")
        resp_raw = requests.post(
            self.acapy_host + CREATE_PRESENTATION_REQUEST_URL,
            headers={
                "X-API-KEY": self.acapy_x_api_key,
                "Authorization": "Bearer " + self.wallet_token,
            },
            json=presentation_request_configuration,
        )
        assert resp_raw.status_code == 200, resp_raw.content
        resp = json.loads(resp_raw.content)

        return resp

    def get_wallet_public_did(self) -> WalletDidPublicResponse:
        resp_raw = requests.get(
            self.acapy_host + WALLET_DID_URI,
            headers={
                "X-API-KEY": self.acapy_x_api_key,
                "Authorization": "Bearer " + self.wallet_token,
            },
        )
        assert (
            resp_raw.status_code == 200
        ), f"{resp_raw.status_code}::{resp_raw.content}"
        resp = json.loads(resp_raw.content)
        result = WalletDidPublicResponse.parse_obj(resp)


        force_did = WalletPublicDid(did="FYAjq8xXorZtexJniU7fzH", verkey="8vZCafo36X1HnM97QiMpf7Ae2Pm4yYJAFZSp2BnN6AaQ", public=True)

        return WalletDidPublicResponse(result=force_did)
