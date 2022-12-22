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

EXAMPLE_COMPLETED_PRESENT_PROOF = {
    "connection_id": "aa90ebdb-f8f7-414d-9189-d0a92d71de50",
    "presentation": {
        "proof": {
            "proofs": [],
            "aggregated_proof": {
                "c_hash": "10091511890843561634965850852551987316055992836281489841119003594123660264717",
                "c_list": [],
            },
        },
        "requested_proof": {
            "revealed_attrs": {},
            "self_attested_attrs": {"attr_0": "first"},
            "unrevealed_attrs": {},
            "predicates": {},
        },
        "identifiers": [],
    },
    "auto_present": False,
    "role": "verifier",
    "presentation_exchange_id": "f8e71f8a-3b53-4d3f-a3b0-b663be1d9965",
    "updated_at": "2022-12-20T23:21:42.118663Z",
    "state": "verified",
    "presentation_request": {
        "nonce": "393340381426039574046368",
        "name": "string",
        "version": "1.0.0",
        "requested_attributes": {
            "attr_0": {
                "restrictions": [{}],
                "name": "first_name",
                "non_revoked": {},
            }
        },
        "requested_predicates": {},
        "non_revoked": {},
    },
    "created_at": "2022-12-20T23:21:21.224447Z",
    "initiator": "self",
    "thread_id": "69d06764-fb09-4597-93a7-7cfa394e597b",
    "trace": False,
    "presentation_request_dict": {
        "@type": "https://didcomm.org/present-proof/1.0/request-presentation",
        "@id": "69d06764-fb09-4597-93a7-7cfa394e597b",
        "request_presentations~attach": [
            {
                "@id": "libindy-request-presentation-0",
                "mime-type": "application/json",
                "data": {
                    "base64": "eyJyZXF1ZXN0ZWRfYXR0cmlidXRlcyI6IHsiYXR0cl8wIjogeyJuYW1lIjogImZpcnN0X25hbWUiLCAibm9uX3Jldm9rZWQiOiB7fSwgInJlc3RyaWN0aW9ucyI6IFt7fV19fSwgInJlcXVlc3RlZF9wcmVkaWNhdGVzIjoge30sICJuYW1lIjogInN0cmluZyIsICJ2ZXJzaW9uIjogIjEuMC4wIiwgIm5vbl9yZXZva2VkIjoge30sICJub25jZSI6ICIzOTMzNDAzODE0MjYwMzk1NzQwNDYzNjgifQ=="
                },
            }
        ],
        "comment": "string",
    },
    "verified": "false",
    "auto_verify": True,
}


class AcapyClient:
    wallet_id = "c6a6cdc2-723d-4368-b249-d046f40a7656"
    acapy_host = "http://traction-agent:8031"
    acapy_x_api_key = "change-me"
    service_endpoint = "https://80aa-165-225-211-70.ngrok.io"  # from ngrok

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

    def create_presentation_request(
        self, presentation_request_configuration: dict
    ) -> CreatePresentationResponse:
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
        result = CreatePresentationResponse.parse_obj(resp)

        logger.info(result)
        logger.debug(f"<<< create_presenation_request")
        return result

    def get_presentation_request(self, presentation_exchange_id: UUID):
        if not self.wallet_token:
            self.get_wallet_token()

        logger.debug(f">>> get_presentation_request")
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

        return resp

    def get_wallet_public_did(self) -> WalletPublicDid:
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

        # force_did = WalletPublicDid(
        #     did="FYAjq8xXorZtexJniU7fzH",
        #     verkey="8vZCafo36X1HnM97QiMpf7Ae2Pm4yYJAFZSp2BnN6AaQ",
        #     posture="public",
        # )

        logger.info(public_did)
        return public_did
