# vc-oidc-auth-service

clone [traction](https://github.com/bcgov/traction) and run `docker-compose up` from `/scripts`

clone [vc-auth-poc](https://github.com/jsyro/vc-auth/poc) and run `PRES_REQ_CONF_ID="test-pres-req" docker-compose up --build -d` from `/vue`

run `docker-compose up` from `/script` of this project

### Prepare Acapy wallet for use

1. Create wallet
2. Create A Public did
   1. create did at @`http://localhost:8031/api/doc#/wallet/post_wallet_did_create`
   2. publish did using website `http://test.bcovrin.vonx.io/`
   3. Set did as public in acapy using @`http://localhost:8031/api/doc#/wallet/post_wallet_did_public`
3. Set Acapy Wallet Webhook URL at @`http://localhost:8031/api/doc#/multitenancy/put_multitenancy_wallet__wallet_id_` with body

```
{
  "image_url": "https://aries.ca/images/sample.png",
  "label": "Alice",
  "wallet_dispatch_type": "default",
  "wallet_webhook_urls": [
    "http://oidc-controller:5000/webhooks"
  ]
}
```

### Prepare Environment Variables for first use

### Prepare controller for use

1. create default verification_configuration @`http://localhost:5201/docs#/ver_configs/create_ver_conf_ver_configs_post`
