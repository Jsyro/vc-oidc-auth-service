ex_hero_read = {
    "ver_config_id": "test-request-config",
    "subject_identifier": "first_name",
    "proof_request": {
        "name": "Basic Proof",
        "version": "1.0",
        "requested_attributes": [
            {"name": "first_name", "restrictions": []},
            {"name": "last_name", "restrictions": []},
        ],
        "requested_predicates": [],
    },
}

ex_hero_create = {
    "ver_config_id": "test-request-config",
    "subject_identifier": "first_name",
    "proof_request": {
        "name": "Basic Proof",
        "version": "1.0",
        "requested_attributes": [
            {"name": "first_name", "restrictions": []},
            {"name": "last_name", "restrictions": []},
        ],
        "requested_predicates": [],
    },
}

ex_hero_patch = {"nickname": "TheLastManStands!", "role": "warrior"}
