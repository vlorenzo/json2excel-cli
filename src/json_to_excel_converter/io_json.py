from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, Optional

import ijson


def _normalize_root_path_to_ijson_prefix(root_path: str | None) -> str:
	"""
	Convert a dotted path like "data.items" or a JSON Pointer like "/data/items"
	into an ijson prefix suitable for ijson.items(..., prefix="<prefix>.item").

	Rules:
	- None or empty means top-level array -> prefix "item"
	- Strip leading "/" for JSON Pointer, then replace "/" with "."
	- Dotted paths remain dotted
	- Resulting prefix will NOT include trailing ".item" (caller appends as needed)
	"""
	if not root_path:
		return ""
	path = root_path.strip()
	if path.startswith("/"):
		path = path.lstrip("/")
	# Remove empty segments (e.g., accidental //)
	segments = [seg for seg in path.replace("/", ".").split(".") if seg]
	return ".".join(segments)


def iter_items(
	json_file: str | Path,
	root_path: Optional[str] = None,
	allow_object_values: bool = False,
) -> Iterator[dict]:
	"""
	Stream JSON records from a large file without loading into memory.

	- If the root points to an array (recommended), yields each element of the array.
	- If allow_object_values is True and the root points to an object, yields each value.

	Parameters:
	- json_file: Path to input JSON file
	- root_path: Dotted path or JSON Pointer to the array/object to iterate
	- allow_object_values: If True, when root points to an object, iterate over its values

	Raises ValueError with helpful guidance when nothing is found at the provided root.
	"""
	json_path = Path(json_file)
	if not json_path.exists():
		raise FileNotFoundError(f"Input JSON file not found: {json_path}")

	prefix_base = _normalize_root_path_to_ijson_prefix(root_path)
	# Determine ijson prefix for array items
	items_prefix = "item" if prefix_base == "" else f"{prefix_base}.item"

	with json_path.open("rb") as f:
		# Try as array first
		yielded_any = False
		for obj in ijson.items(f, items_prefix):
			yielded_any = True
			yield obj  # type: ignore[misc]

		if yielded_any:
			return

		# If no items yielded, consider object values when allowed
		if allow_object_values:
			# For objects, use kvitems to get values under the object root
			f.seek(0)
			object_prefix = prefix_base
			if not object_prefix:
				# top-level object
				object_prefix = ""
			values_iter = (
				value
				for _key, value in ijson.kvitems(f, object_prefix)  # type: ignore[arg-type]
			)
			count = 0
			for value in values_iter:
				count += 1
				if isinstance(value, dict):
					yield value
				else:
					# Produce dict for scalar values to keep a consistent interface
					yield {"value": value}
			if count:
				return

	# Neither array items nor object values were found
	raise ValueError(
		"No items found at the given root path. "
		"Ensure the root points to an array (recommended), or pass allow_object_values=True for objects. "
		f"Root provided: {root_path!r}"
	)
