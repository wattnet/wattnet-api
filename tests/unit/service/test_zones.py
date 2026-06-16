"""
Unit tests for wattnet.api.service.zones module.

These tests validate:
- Correct merging of zone metadata with crossborder neighbours
- Alphabetical sorting of the returned list
- Fallback to empty neighbours when zone absent from crossborders file
- Provider normalisation mapping and rejection of unknown providers
- YAML loader validation (must be a list)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from wattnet.api.service.zones import ZoneService

# ============================================================
# Helpers
# ============================================================


def _write_yaml(path: Path, data: object) -> None:
    """Serialise *data* as YAML and write it to *path*.

    :param path: Destination file path
    :type path: Path
    :param data: Python object to serialise
    :type data: object
    :return: None
    :rtype: None
    """
    path.write_text(yaml.dump(data), encoding="utf-8")


def _make_zone_entry(
    zone_id: str = "ES",
    full_name: str = "Spain",
    eic_code: str = "10YES-REE------0",
    country_code: str = "ESP",
    country_name: str = "Spain",
    provider: str = "entsoe",
) -> dict:
    """Return a minimal zone YAML entry dict.

    :param zone_id: Zone code
    :param full_name: Full descriptive name
    :param eic_code: EIC code string
    :param country_code: ISO 3166-1 alpha-3 country code
    :param country_name: Country name
    :param provider: Raw provider key
    :return: Zone entry dict
    :rtype: dict
    """
    return {
        "zone_id": zone_id,
        "full_name": full_name,
        "eic_code": eic_code,
        "country_code": country_code,
        "country_name": country_name,
        "provider": provider,
    }


def _make_service(
    tmp_path: Path,
    zones: list,
    crossborders: list,
) -> ZoneService:
    """Write YAML fixtures and return a configured ZoneService.

    :param tmp_path: Temporary directory
    :param zones: Zone list data
    :param crossborders: Crossborder list data
    :return: Configured ZoneService
    :rtype: ZoneService
    """
    zones_file = tmp_path / "zones.yaml"
    cross_file = tmp_path / "crossborders.yaml"
    _write_yaml(zones_file, zones)
    _write_yaml(cross_file, crossborders)
    return ZoneService(zones_file_path=zones_file, crossborders_file_path=cross_file)


# ============================================================
# get_zones — sorting
# ============================================================


def test_get_zones_sorted_alphabetically(tmp_path: Path) -> None:
    """Returned zones must be sorted by zone code in ascending order.

    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    zones = [
        _make_zone_entry("PT"),
        _make_zone_entry("ES"),
        _make_zone_entry("FR"),
    ]
    svc = _make_service(tmp_path, zones, crossborders=[])

    result = svc.get_zones()

    codes = [z.zone for z in result]
    assert codes == sorted(codes)


# ============================================================
# get_zones — neighbours merging
# ============================================================


def test_get_zones_merges_neighbours(tmp_path: Path) -> None:
    """Zones must carry the neighbours declared in the crossborders file.

    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    zones = [_make_zone_entry("ES")]
    crossborders = [{"zone_id": "ES", "neighbours": ["FR", "PT"]}]
    svc = _make_service(tmp_path, zones, crossborders)

    result = svc.get_zones()

    assert sorted(result[0].neighbours) == ["FR", "PT"]


def test_get_zones_empty_neighbours_when_absent_from_crossborders(
    tmp_path: Path,
) -> None:
    """Zones not listed in crossborders must get an empty neighbours list.

    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    zones = [_make_zone_entry("ES")]
    svc = _make_service(tmp_path, zones, crossborders=[])

    result = svc.get_zones()

    assert result[0].neighbours == []


def test_get_zones_returns_correct_provider(tmp_path: Path) -> None:
    """Provider must be normalised to the canonical API representation.

    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    zones = [_make_zone_entry("ES", provider="entsoe")]
    svc = _make_service(tmp_path, zones, crossborders=[])

    result = svc.get_zones()

    assert result[0].provider == "ENTSO-E"


# ============================================================
# _normalize_provider
# ============================================================


def test_normalize_provider_entsoe() -> None:
    """'entsoe' must map to 'ENTSO-E'.

    :return: None
    :rtype: None
    """
    assert ZoneService._normalize_provider("entsoe") == "ENTSO-E"


def test_normalize_provider_elexon() -> None:
    """'elexon' must map to 'Elexon'.

    :return: None
    :rtype: None
    """
    assert ZoneService._normalize_provider("elexon") == "Elexon"


def test_normalize_provider_epias() -> None:
    """'epias' must map to 'EPIAS'.

    :return: None
    :rtype: None
    """
    assert ZoneService._normalize_provider("epias") == "EPIAS"


def test_normalize_provider_unknown_raises() -> None:
    """Unknown provider key must raise ValueError.

    :return: None
    :rtype: None
    """
    with pytest.raises(ValueError, match="Unsupported provider"):
        ZoneService._normalize_provider("opendata")


# ============================================================
# _read_yaml_list
# ============================================================


def test_read_yaml_list_raises_when_not_list(tmp_path: Path) -> None:
    """A YAML file containing a mapping (not a list) must raise ValueError.

    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    bad_file = tmp_path / "bad.yaml"
    _write_yaml(bad_file, {"key": "value"})

    with pytest.raises(ValueError, match="must contain a list"):
        ZoneService._read_yaml_list(bad_file)


def test_read_yaml_list_returns_list(tmp_path: Path) -> None:
    """A valid YAML list file must be returned as a Python list.

    :param tmp_path: Temporary directory fixture
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    data = [{"zone_id": "ES"}, {"zone_id": "FR"}]
    valid_file = tmp_path / "valid.yaml"
    _write_yaml(valid_file, data)

    result = ZoneService._read_yaml_list(valid_file)

    assert result == data
