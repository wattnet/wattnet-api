"""Check that an OpenAPI document only adds to an older one.

The older document is the contract that clients already rely on. The new one may
add paths, parameters, properties, enum values, responses and schemas, and may mark
things as deprecated, but whatever the old one says must still be there and mean the
same. Descriptions, titles and examples are free text and are not compared.
"""

from __future__ import annotations

from typing import Any, Dict, List

# Free text and markers that can change without touching what a client sends or reads.
IGNORED_KEYS = {
    "description",
    "title",
    "summary",
    "example",
    "examples",
    "deprecated",
    "info",
    "servers",
    "externalDocs",
    "tags",
    "required",  # handled for parameters; the list of a schema is only about reads
}


def _resolve(node: Any, spec: Dict[str, Any]) -> Any:
    """Follow ``$ref`` pointers inside the same document."""
    while isinstance(node, dict) and "$ref" in node:
        target: Any = spec
        for part in node["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        node = target
    return node


def _key(item: Any) -> Any:
    """Identify an item of a list of objects (a parameter is its name and place)."""
    if isinstance(item, dict) and "name" in item and "in" in item:
        return (item["name"], item["in"])
    return None


def breaks(
    old: Any, new: Any, old_spec: Dict, new_spec: Dict, path: str = ""
) -> List[str]:
    """Return what the old document says that the new one no longer says.

    :param old: node of the old document
    :param new: node of the new document
    :param old_spec: whole old document, to resolve its references
    :param new_spec: whole new document, to resolve its references
    :param path: where we are, for the messages
    :return: list of differences, empty when the new one only adds
    """
    old, new = _resolve(old, old_spec), _resolve(new, new_spec)
    if isinstance(old, dict):
        if not isinstance(new, dict):
            return [f"{path}: was an object"]
        found: List[str] = []
        for k, v in old.items():
            if k in IGNORED_KEYS:
                continue
            if k not in new:
                found.append(f"{path}/{k}: removed")
            elif k == "enum":
                missing = [x for x in v if x not in new[k]]
                found += [f"{path}/enum: lost {missing}"] if missing else []
            else:
                found += breaks(v, new[k], old_spec, new_spec, f"{path}/{k}")
        return found
    if isinstance(old, list):
        if not isinstance(new, list):
            return [f"{path}: was a list"]
        found = []
        for i, item in enumerate(old):
            ident = _key(item)
            if ident is not None:
                match = next((n for n in new if _key(n) == ident), None)
                if match is None:
                    found.append(f"{path}: parameter {ident} removed")
                    continue
                if isinstance(item, dict) and item.get("required") is False:
                    if match.get("required") is True:
                        found.append(f"{path}: parameter {ident} became required")
                found += breaks(item, match, old_spec, new_spec, f"{path}[{ident[0]}]")
            elif isinstance(item, dict):
                # anyOf / oneOf / allOf / prefixItems: some option of the new one must hold
                if not any(not breaks(item, n, old_spec, new_spec, "") for n in new):
                    found.append(f"{path}[{i}]: no longer matched")
            elif item not in new:
                found.append(f"{path}: lost {item!r}")
        return found
    return [] if old == new else [f"{path}: {old!r} is now {new!r}"]
