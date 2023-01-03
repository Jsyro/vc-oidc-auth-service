import requests
import json
import logging
from uuid import UUID

from .models import WalletDidPublicResponse, WalletPublicDid, CreatePresentationResponse

from api.db.models.presentation_request_config import PresentationRequestConfiguration

_client = None
logger = logging.getLogger(__name__)

WALLET_DID_URI = "/wallet/did/public"
CREATE_PRESENTATION_REQUEST_URL = "/present-proof/create-request"
PRESENT_PROOF_RECORDS = "/present-proof/records"


class AcapyClient:
    wallet_id = "c6a6cdc2-723d-4368-b249-d046f40a7656"
    acapy_host = "http://traction-agent:8031"
    acapy_x_api_key = "change-me"
    service_endpoint = (
        "https://5d89-165-225-211-70.ngrok.io"  # from ngrok traction-agent
    )

    # wallet_id = "30d938ed-2708-46b7-860e-1a1b77ad7da4"
    # acapy_host = "https://traction-acapy-admin-test.apps.silver.devops.gov.bc.ca/"
    # acapy_x_api_key = "b4pFHeTJvRqRMAi11SCSaYjcL8KjcNhZ"

    # wallet_id = "3bf7500b-c0bd-461d-96a7-999d16ce1bb5"
    # acapy_host = "https://int-traction-acapy-admin-test.apps.silver.devops.gov.bc.ca"
    # acapy_x_api_key = "Vlp07FJzVjEY9xAU0YskghPdOODAvoUg"
    # service_endpoint = (
    #     "https://int-traction-acapy-test.apps.silver.devops.gov.bc.ca"  # from ngrok
    # )

    wallet_token: str = None

    def __init__(self):
        if _client:
            return _client
        super().__init__()

    def get_wallet_token(self):
        logger.debug(f">>> get_wallet_token")
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
        logger.debug(f"<<< get_wallet_token")

        return self.wallet_token

    def create_presentation_request(
        self, presentation_request_configuration: dict
    ) -> CreatePresentationResponse:
        logger.debug(f">>> create_presentation_request")
        if not self.wallet_token:
            self.get_wallet_token()

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
        result = CreatePresentationResponse.parse_obj(resp)

        logger.debug(f"<<< create_presenation_request")
        return result

    def get_presentation_request(self, presentation_exchange_id: UUID):
        logger.debug(f">>> get_presentation_request")
        if not self.wallet_token:
            self.get_wallet_token()

        resp_raw = requests.get(
            self.acapy_host
            + PRESENT_PROOF_RECORDS
            + "/"
            + str(presentation_exchange_id),
            headers={
                "X-API-KEY": self.acapy_x_api_key,
                "Authorization": "Bearer " + self.wallet_token,
            },
        )
        assert resp_raw.status_code == 200, resp_raw.content
        resp = json.loads(resp_raw.content)

        logger.debug(f"<<< get_presentation_request -> {resp}")
        return resp

    def verify_presentation(self, presentation_exchange_id: UUID):
        logger.debug(f">>> verify_presentation")
        if not self.wallet_token:
            self.get_wallet_token()

        resp_raw = requests.post(
            self.acapy_host
            + PRESENT_PROOF_RECORDS
            + "/"
            + str(presentation_exchange_id)
            + "/verify-presentation",
            headers={
                "X-API-KEY": self.acapy_x_api_key,
                "Authorization": "Bearer " + self.wallet_token,
            },
        )
        assert resp_raw.status_code == 200, resp_raw.content
        resp = json.loads(resp_raw.content)

        logger.debug(f"<<< verify_presentation -> {resp}")
        return resp

    def get_wallet_public_did(self) -> WalletPublicDid:
        logger.debug(f">>> get_wallet_public_did")

        if not self.wallet_token:
            self.get_wallet_token()
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
        public_did = WalletPublicDid.parse_obj(resp["result"])

        logger.debug(f"<<< get_wallet_public_did -> {public_did}")
        return public_did
