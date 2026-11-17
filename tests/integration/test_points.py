"""The OpenAPI document of the series: ``values`` is deprecated and ``points`` replaces it."""

from __future__ import annotations


def test_values_are_deprecated_and_points_are_declared(client) -> None:
    """Every schema with ``values`` marks it deprecated and also declares ``points``.

    :return: None
    :rtype: None
    """
    schemas = client.get("/v1/openapi.json").json()["components"]["schemas"]
    with_values = {
        n: s for n, s in schemas.items() if "values" in s.get("properties", {})
    }
    assert len(with_values) == 13
    for name, schema in with_values.items():
        props = schema["properties"]
        assert props["values"]["deprecated"] is True, name
        assert "deprecated" not in props["points"], name
        assert props["points"]["items"]["$ref"].endswith("/Point"), name
        assert "points" in schema["required"] or name == "FactorSeries", name
