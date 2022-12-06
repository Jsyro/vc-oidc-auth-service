import logging
import requests
import json

from .acapy import wallet_id, wallet_key

logger = logging.getLogger(__name__)
_client = None


class TractionClient:
    traction_url = "http://localhost:5100"
    url_prefix = "/tenant"

    def __init__(self):
        if _client:
            return _client
        super().__init__()

    def create_dev_tenant(self):
        logger.info(f">>> create_dev_tenant")
        resp_raw = requests.post(
            self.traction_url + "/innkeeper/token",
            data={"username": "innkeeper", "password": "change-me"},
        )
        resp = json.loads(resp_raw.content)
        print(resp)
        resp_raw = requests.post(
            self.traction_url + "/innkeeper/check-in",
            data={"name": "oidc-tenant", "allow_issue_credentials": "false"},
        )
        resp = json.loads(resp_raw.content)

        self.wallet_id = resp["wallet_id"]
        self.wallet_key = resp["wallet_key"]
        pass

    def get_access_token(self):
        logger.info(f">>> get_access_token")
        resp_raw = requests.post(
            self.traction_url + self.url_prefix + "/token",
            data={"username": self.wallet_id, "password": self.wallet_key},
        )
        resp = json.loads(resp_raw.content)
        self.tenant_token = resp["access_token"]
        return self.tenant_token
s

    def get_request_headers(self):
        logger.info(f">>> get_request_headers")
        if not self.tenant_token:
            self.get_access_token()
        return {"Authorization": "Bearer " + self.tenant_token}

    def create_presentation_request(self):
        logger.info(f">>> create_presentation_request")

        req_dict = {
            "proof_request": {
                "requested_attributes": [
                    {
                        "name": "first_name",
                        "non_revoked": {},
                        "restrictions": [{}],
                    },
                    {
                        "name": "last_name",
                        "non_revoked": {},
                        "restrictions": [{}],
                    },
                ],
                "requested_predicates": [],
                "non_revoked": {},
            },
            "name": "test_pres_conf",
            "version": "1.0.0",
        }
        req_headers = self.get_request_headers()
        print(req_headers)

        # TRACTION REQUIRES CONNECTIONS
        """
        resp_raw = requests.post(
            self.traction_url
            + self.url_prefix
            + "/v1/verifier/presentations/adhoc-request",
            headers=req_headers,
            json=req_dict,
        )
        """
        resp_raw = requests.post(
            self.acapy_host,
        )

        resp = json.loads(resp_raw.content)
        print(resp)
