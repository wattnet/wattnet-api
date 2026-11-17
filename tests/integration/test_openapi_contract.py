"""The OpenAPI document of /v1 only adds to the saved contract.

``tests/contract/openapi-v1.json`` is the contract that clients rely on. This test
fails when a path, a parameter, a response property, an enum value or a type is removed
or changed. To change the contract on purpose, regenerate it in the same pull request
(the diff of the file shows what changed for the clients)::

    UPDATE_OPENAPI_CONTRACT=1 pytest tests/integration/test_openapi_contract.py
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path

from tests.contract.openapi_compat import breaks

_CONTRACT = Path(__file__).parent.parent / "contract" / "openapi-v1.json"


def _current(client) -> dict:
    spec = client.get("/v1/openapi.json").json()
    spec["info"].pop("version", None)  # it is the commit of the build
    return spec


def test_openapi_only_adds_to_the_contract(client) -> None:
    """Nothing the saved contract says has been removed or changed.

    :return: None
    :rtype: None
    """
    current = _current(client)
    if os.environ.get("UPDATE_OPENAPI_CONTRACT"):
        _CONTRACT.write_text(json.dumps(current, indent=1, sort_keys=True) + "\n")
    saved = json.loads(_CONTRACT.read_text())
    assert breaks(saved, current, saved, current) == []


def test_the_check_notices_what_a_client_would_notice() -> None:
    """The check fails for a removed path, parameter, property and enum value.

    :return: None
    :rtype: None
    """
    old = {
        "paths": {
            "/a": {
                "get": {
                    "parameters": [{"name": "zone", "in": "query", "required": False}]
                }
            }
        },
        "components": {
            "schemas": {
                "S": {
                    "type": "object",
                    "properties": {"x": {"type": "string", "enum": ["a", "b"]}},
                }
            }
        },
    }
    assert breaks(old, old, old, old) == []

    def changed(edit) -> dict:
        new = copy.deepcopy(old)
        edit(new)
        return new

    x = lambda n: n["components"]["schemas"]["S"]["properties"]["x"]  # noqa: E731
    param = lambda n: n["paths"]["/a"]["get"]["parameters"]  # noqa: E731
    for broken in (
        changed(lambda n: n["paths"].clear()),
        changed(lambda n: param(n).clear()),
        changed(lambda n: param(n)[0].update(required=True)),
        changed(lambda n: x(n).update(enum=["a"])),
        changed(lambda n: x(n).update(type="integer")),
        changed(lambda n: n["components"]["schemas"]["S"]["properties"].pop("x")),
    ):
        assert breaks(old, broken, old, broken)

    def add(n) -> None:
        n["components"]["schemas"]["S"]["properties"]["y"] = {"type": "string"}
        x(n)["enum"] = ["a", "b", "c"]
        x(n)["deprecated"] = True
        n["paths"]["/b"] = {"get": {}}

    added = changed(add)
    assert breaks(old, added, old, added) == []
