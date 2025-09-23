# JSON to Excel Converter

Convert large JSON to CSV/XLSX with root selection, flattening, array explode, exclusion, and header control.

- User Guide: [docs/guide.md](docs/guide.md)
- Technical Notes: [docs/tech.md](docs/tech.md)
- Examples: [examples/commands.md](examples/commands.md)

## Features
- Streams JSON using `ijson` (no need to load entire file)
- Choose root node (dotted path or JSON Pointer)
- Flatten nested objects with a custom separator
- Options for list handling: join scalars, JSON-encode; explode specific paths into rows
- Write CSV or XLSX, with header sampling
- Control header ordering and pin selected columns to the front
- Exclude nested properties by dotted path prefix

## Install (using uv)
```bash
uv sync
```

## CLI
```bash
. .venv/bin/activate
json-to-excel-converter INPUT.json OUTPUT.(csv|xlsx) \
  --root items \
  --explode attributes \
  --list-policy join \
  --list-sep "," \
  --sep . \
  --sheet-name Items \
  --sample-headers 1000 \
  --header-order stable \
  --first-column id \
  --exclude details
```

### Options
- `--root`: dotted or JSON Pointer path to array/object to iterate.
- `--explode` (repeatable): dotted paths to arrays to explode into rows (cartesian product if multiple).
- `--list-policy`: how to handle lists that are not exploded (`join` or `json`).
- `--list-sep`: used for `join` policy of scalar lists.
- `--allow-object-values`: iterate over object values if `--root` points to an object.
- `--sample-headers`: how many rows to peek to build headers; increase for very heterogeneous data.
- `--header-order`: `stable` (first-seen order; default) or `alpha` (alphabetical after pinned columns).
- `--first-column` (repeatable): pin columns to the beginning in the given order.
- `--exclude` (repeatable): drop any column whose dotted name equals or starts with the given prefix.

## Examples
- Flat rows per item (CSV):
```bash
json-to-excel-converter examples/ads_small.json out.csv --root items
```

- Explode nested arrays and keep IDs first:
```bash
json-to-excel-converter examples/ads_small.json out.xlsx \
  --root items \
  --explode attributes \
  --first-column id \
  --header-order stable
```

- Exclude a subtree:
```bash
json-to-excel-converter examples/ads_small.json out.csv \
  --root items \
  --exclude details
```

## Library usage
```python
from json_to_excel_converter.io_json import iter_items
from json_to_excel_converter.flatten import flatten_record
from json_to_excel_converter.io_table import write_csv

rows = (
    row
    for rec in iter_items("input.json", root_path="items")
    for row in flatten_record(rec, sep=",", explode_paths=["attributes"]) 
)
write_csv(rows, "out.csv", pre_headers=["id"], header_order="stable")
```

## Tests
```bash
uv run pytest -q
# Run only CLI tests
uv run pytest -q tests/cli
```
