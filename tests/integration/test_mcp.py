"""The MCP interface: the tools, the tiers and the errors, against the REST ones."""

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from tests.unit.service.helpers import FakeMetric
from tests.unit.test_access import POLICY
from wattnet.api import access
from wattnet.api.access import PolicyFile
from wattnet.api.mcp.tools import ALL_TOOLS
from wattnet.api.rest.v1 import api_router_v1

HEADERS = {"accept": "application/json, text/event-stream"}


def rpc(client, method, params=None, tier=None, id=1):
    headers = {**HEADERS, **({"X-Wattnet-Tier": tier} if tier else {})}
    body = {"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}}
    return client.post("/mcp", json=body, headers=headers)


def call(client, name, arguments=None, tier=None):
    r = rpc(client, "tools/call", {"name": name, "arguments": arguments or {}}, tier)
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture(scope="module")
def mcp_client():
    from wattnet.api.main import versioned_app

    with TestClient(versioned_app) as c:  # enters the lifespan of the MCP manager
        yield c


def test_initialize(mcp_client):
    r = rpc(
        mcp_client,
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "t", "version": "1"},
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["result"]["serverInfo"]["name"] == "Wattnet"


def test_every_data_route_has_a_tool(mcp_client):
    offered = {s.handler for s in ALL_TOOLS}
    routes = {
        r.endpoint
        for r in api_router_v1.routes
        if hasattr(r, "endpoint") and "/status/" not in r.path
    }
    assert routes - offered == set()


def test_tools_list(mcp_client):
    tools = rpc(mcp_client, "tools/list").json()["result"]["tools"]
    assert {t["name"] for t in tools} == {s.name for s in ALL_TOOLS}
    mix = next(t for t in tools if t["name"] == "get_mix")
    assert "zone" in mix["inputSchema"]["properties"]
    assert mix["description"]


_NOW = datetime(2025, 6, 1, tzinfo=timezone.utc)


def _mix(**kw):
    meta = {
        "zone": "ES",
        "unit": "MW",
        "production_type": "solar",
        "data_state": "official",
        "datasource": "flow_tracing",
        "valid": True,
        "zone_status": "complete",
    }
    return FakeMetric(_NOW, 200.0, {**meta, **kw})


def _fmt(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _window(days, ago=1):
    end = datetime.now(timezone.utc) - timedelta(days=ago)
    return {"start": _fmt(end - timedelta(days=days)), "end": _fmt(end)}


@pytest.fixture
def with_policy(monkeypatch, tmp_path):
    path = tmp_path / "access-policy.yaml"
    path.write_text(POLICY)
    monkeypatch.setattr(access, "policy", PolicyFile(path))


def _error(result):
    """Return the {code, detail, status} of a failed tool call, or None."""
    res = result["result"]
    if not res.get("isError"):
        return None
    text = res["content"][0]["text"]  # the SDK puts a prefix before our JSON
    return json.loads(text[text.index("{") :])


def test_a_tool_returns_what_the_storage_has(mcp_client, mock_db):
    mock_db([_mix()])
    res = call(mcp_client, "get_mix", {"zone": "es"})["result"]
    assert not res.get("isError")
    body = res["structuredContent"]["result"]
    assert body[0]["zone"] == "ES"
    assert body[0]["series"][0]["production"][0]["production_type"] == "solar"


def test_no_data_is_an_empty_answer(mcp_client, mock_db):
    mock_db([])
    res = call(mcp_client, "get_mix", {"zone": "ES"})["result"]
    assert not res.get("isError") and res["structuredContent"]["result"] == []


def test_the_coordinates_find_the_zone(mcp_client, mock_db, mock_geo):
    mock_db([_mix(zone="PT")])
    mock_geo("PT")
    res = call(mcp_client, "get_mix", {"lat": 38.7, "lon": -9.1})["result"]
    assert res["structuredContent"]["result"][0]["zone"] == "PT"


def test_a_place_without_zone_is_an_error_with_code(mcp_client, mock_db, mock_geo):
    mock_db([])
    mock_geo(None)
    err = _error(call(mcp_client, "get_mix", {"lat": 0.0, "lon": 0.0}))
    assert err["status"] == 404 and err["code"] == "zone_not_found_for_coordinates"


def test_invalid_parameters_are_errors_with_the_rest_code(mcp_client, mock_db):
    mock_db([])
    err = _error(call(mcp_client, "get_mix", {"zone": "ES", "resolution": "5m"}))
    assert err["code"] == "invalid_resolution" and err["status"] == 400
    err = _error(call(mcp_client, "get_mix", {"zone": "ES", "production_type": "x"}))
    assert err["status"] == 400


def test_out_of_range_latitude_is_refused_by_the_schema(mcp_client, mock_db):
    mock_db([])
    r = call(mcp_client, "get_mix", {"lat": 200, "lon": 0})
    assert "error" in r or r["result"].get("isError")


def test_a_failure_of_the_storage_does_not_leak(mcp_client, monkeypatch):
    def boom(self, *a, **k):
        raise RuntimeError("clickhouse password=secret")

    monkeypatch.setattr(
        "wattnet.storage.repository.MetricsRepository.query_metrics", boom
    )
    err = _error(call(mcp_client, "get_mix", {"zone": "ES"}))
    assert err["code"] == "internal_error" and "secret" not in json.dumps(err)


def test_list_zones_and_status(mcp_client, monkeypatch):
    monkeypatch.setattr("wattnet.api.rest.v1.zones.zone_service.get_zones", lambda: [])
    assert not call(mcp_client, "list_zones")["result"].get("isError")
    monkeypatch.setattr("wattnet.api.rest.v1.status.check_storage_system", lambda: True)
    assert not call(mcp_client, "get_status")["result"].get("isError")


TIERS = [None, "nobody", "free", "research", "internal"]

# (tool, REST url, arguments): the same query on both interfaces
CASES = [
    ("get_mix", "/v1/mix", {"zone": "ES"}),
    ("get_mix", "/v1/mix", {}),
    ("get_mix", "/v1/mix", {"zone": "ES", **_window(3)}),
    ("get_mix", "/v1/mix", {"zone": "ES", **_window(10)}),
    ("get_mix", "/v1/mix", {"zone": "ES", **_window(2, ago=20)}),
    ("get_mix", "/v1/mix", {"zone": "ES", **_window(500)}),
    ("get_mix", "/v1/mix", {**_window(31)}),
    ("get_mix_share", "/v1/mix-share", {"zone": "ES"}),
    ("get_factors", "/v1/factors", {}),
    ("get_footprints", "/v1/footprints", {"zone": "ES"}),
    ("list_zones", "/v1/zones", {}),
]


@pytest.mark.parametrize("tier", TIERS)
@pytest.mark.parametrize("tool,url,args", CASES)
def test_mcp_applies_the_tiers_as_rest_does(
    mcp_client, client, with_policy, mock_db, monkeypatch, tool, url, args, tier
):
    """Same credentials, same query: the same answer, or the same refusal code."""
    mock_db([])
    monkeypatch.setattr("wattnet.api.rest.v1.zones.zone_service.get_zones", lambda: [])
    headers = {"X-Wattnet-Tier": tier} if tier else {}
    rest = client.get(url, params=args, headers=headers)
    err = _error(call(mcp_client, tool, args, tier))
    if rest.status_code == 200:
        assert err is None
    else:
        assert err is not None
        assert err["code"] == rest.json()["code"]
        assert err["status"] == rest.status_code


def test_without_a_policy_mcp_has_no_tiers_but_the_size_cap(
    mcp_client, mock_db, monkeypatch
):
    mock_db([])
    monkeypatch.setattr(access, "policy", None)
    assert _error(call(mcp_client, "get_mix", {})) is None
    err = _error(call(mcp_client, "get_mix", {"zone": "ES", **_window(500)}))
    assert err["code"] == "query_too_big"
