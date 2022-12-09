import requests
import json
import logging


_client = None
logger = logging.getLogger(__name__)

wallet_id = "6d506247-5bdb-4662-9309-824e85bdf712"
wallet_key = "123b9468-38af-4896-9bb6-f33881387a79"


class AcapyClient:
    acapy_host = "http://host.docker.internal:8031"
    acapy_x_api_key = "change-me"

    wallet_token: str = None

    def __init__(self):
        if _client:
            return _client
        super().__init__()

    def get_wallet_token(self):
        global wallet_key
        logger.info(f">>> get_wallet_token")
        resp_raw = requests.post(
            self.acapy_host + f"/multitenancy/wallet/{wallet_id}/token",
            data={"wallet_key": wallet_key},
            headers={"X-API-KEY": self.acapy_x_api_key},
        )
        assert resp_raw.status_code == 200, resp_raw.status_code
        resp = json.loads(resp_raw.content)
        self.wallet_token = resp["token"]
        return self.wallet_token

    def create_presentation_request(self):
        if not self.wallet_token:
            self.get_wallet_token()

        req_dict = {
            "auto_verify": False,
            "comment": "string",
            "proof_request": {
                "name": "Proof request",
                "requested_attributes": {
                    "prop1": {
                        "name": "first_name",
                        "non_revoked": {},
                        "restrictions": [],
                    },
                    "prop2": {
                        "name": "last_name",
                        "non_revoked": {},
                        "restrictions": [],
                    },
                },
                "requested_predicates": {},
                "non_revoked": {},
            },
            "name": "test_pres_conf",
            "version": "1.0.0",
        }

        logger.debug(f">>> create_presentation_request")
        resp_raw = requests.post(
            self.acapy_host + f"/present-proof/create-request",
            headers={
                "X-API-KEY": self.acapy_x_api_key,
                "Authorization": "Bearer " + self.wallet_token,
            },
            json=req_dict,
        )
        assert resp_raw.status_code == 200, resp_raw.content
        resp = json.loads(resp_raw.content)

        return resp
