from __future__ import annotations

from itertools import product
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence
from decimal import Decimal
import orjson


class ListPolicy:
    JOIN = "join"
    JSON = "json"
    # EXPLODE is handled via explode_paths argument


def _is_scalar(value: Any) -> bool:
    # Treat Decimal as a scalar
    return isinstance(value, (str, int, float, bool, Decimal)) or value is None


def _join_scalars(values: Sequence[Any], separator: str) -> str:
    return separator.join("" if v is None else str(v) for v in values)


def _json_dumps_safe(value: Any) -> str:
    """JSON-encode with Decimal support and safe fallback to str() for unknown types."""
    try:
        return orjson.dumps(value).decode("utf-8")
    except TypeError:
        def default(obj: Any) -> Any:
            if isinstance(obj, Decimal):
                # Preserve numeric meaning
                try:
                    return float(obj)
                except Exception:
                    return str(obj)
            return str(obj)

        return orjson.dumps(value, default=default).decode("utf-8")


def _flatten_mapping(
    obj: Mapping[str, Any],
    parent_key: str = "",
    sep: str = ".",
    list_policy: str = ListPolicy.JOIN,
    list_separator: str = ";",
    explode_paths: set[str] | None = None,
) -> Dict[str, Any]:
    """
    Flatten a nested mapping into a single-level dict, excluding explode paths.

    Lists are handled according to list_policy unless the current key path is slated
    for exploding (handled by the caller). Explode paths are left as-is for the
    caller to process.
    """
    items: Dict[str, Any] = {}
    explode_paths = explode_paths or set()

    for key, value in obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else str(key)
        # Skip flattening here if this path will be exploded later
        if new_key in explode_paths:
            items[new_key] = value
            continue

        if isinstance(value, Mapping):
            items.update(
                _flatten_mapping(
                    value,
                    parent_key=new_key,
                    sep=sep,
                    list_policy=list_policy,
                    list_separator=list_separator,
                    explode_paths=explode_paths,
                )
            )
        elif isinstance(value, list):
            # Lists of dicts or scalars: handle per policy
            if list_policy == ListPolicy.JSON:
                items[new_key] = _json_dumps_safe(value)
            else:
                # JOIN policy
                if all(_is_scalar(v) for v in value):
                    items[new_key] = _join_scalars(value, list_separator)
                else:
                    # Mixed or list of dicts: JSON-encode as a safe fallback
                    items[new_key] = _json_dumps_safe(value)
        else:
            items[new_key] = value

    return items


def _flatten_single_object(obj: Any, prefix: str, sep: str) -> Dict[str, Any]:
    """Flatten a single object (dict or scalar) under a given prefix key."""
    if isinstance(obj, Mapping):
        return _flatten_mapping(obj, parent_key=prefix, sep=sep)
    # Scalar
    return {prefix: obj}


def flatten_record(
    record: Mapping[str, Any],
    *,
    sep: str = ".",
    list_policy: str = ListPolicy.JOIN,
    list_separator: str = ";",
    explode_paths: Iterable[str] | None = None,
) -> List[Dict[str, Any]]:
    """
    Flatten a single record (dict) into one or more flat rows.

    - Nested dicts are flattened using the provided separator.
    - Lists are joined or JSON-encoded depending on list_policy.
    - explode_paths: list of dotted key paths to arrays that should be exploded
      (creating multiple rows). Multiple explode paths will create a cartesian
      product across their elements.

    Returns a list of row dicts because explode can create multiple rows per record.
    """
    if not isinstance(record, Mapping):
        # Attempt to coerce into Mapping or wrap as value
        return [
            {"value": record}
        ]

    explode_set = set(explode_paths or [])

    # First pass: flatten everything except explode paths
    base_flat = _flatten_mapping(
        record,
        parent_key="",
        sep=sep,
        list_policy=list_policy,
        list_separator=list_separator,
        explode_paths=explode_set,
    )

    # Collect expansions for each explode path
    expansions: List[List[Dict[str, Any]]] = []
    for path in explode_set:
        value = base_flat.pop(path, None)
        # If value wasn't present in base_flat, fetch from original record via traversal
        if value is None:
            # Traverse original record to find path
            cursor: Any = record
            for part in path.split(sep):
                if isinstance(cursor, Mapping) and part in cursor:
                    cursor = cursor[part]
                else:
                    cursor = None
                    break
            value = cursor

        if value is None:
            # No values -> treat as single empty expansion
            expansions.append([{}])
            continue

        if isinstance(value, list):
            rows_for_this_path: List[Dict[str, Any]] = []
            for item in value:
                rows_for_this_path.append(_flatten_single_object(item, prefix=path, sep=sep))
            if not rows_for_this_path:
                rows_for_this_path = [{}]
            expansions.append(rows_for_this_path)
        else:
            # Value is scalar or mapping -> single expansion
            expansions.append([_flatten_single_object(value, prefix=path, sep=sep)])

    # Combine base_flat with cartesian product of expansions
    if not expansions:
        return [base_flat]

    combined_rows: List[Dict[str, Any]] = []
    for combo in product(*expansions):
        combined: Dict[str, Any] = dict(base_flat)
        for part in combo:
            combined.update(part)
        combined_rows.append(combined)
    return combined_rows
