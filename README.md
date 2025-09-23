# JSON to Excel Converter

Convert large JSON files to flat tabular formats (CSV/XLSX) with streaming, configurable flattening, and list handling.

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
  --root data.items \
  --explode orders \
  --list-policy join \
  --list-sep "," \
  --sep . \
  --sheet-name Sheet1 \
  --sample-headers 1000 \
  --header-order stable \
  --first-column Vid --first-column DealerId \
  --exclude Advertiser --exclude Eurotax.Options.Serie
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
- Flat rows per ad (CSV):
```bash
json-to-excel-converter data.json out.csv --root Ads
```

- Explode nested arrays and keep IDs first:
```bash
json-to-excel-converter data.json out.xlsx \
  --root Ads \
  --explode Options --explode Eurotax.Options.Serie \
  --first-column Vid --first-column DealerId \
  --header-order stable
```

- Exclude advertiser and Eurotax Serie details:
```bash
json-to-excel-converter data.json out.csv \
  --root Ads \
  --exclude Advertiser --exclude Eurotax.Options.Serie
```

## Library usage
```python
from json_to_excel_converter.io_json import iter_items
from json_to_excel_converter.flatten import flatten_record
from json_to_excel_converter.io_table import write_csv

rows = (
    row
    for rec in iter_items("input.json", root_path="data.items")
    for row in flatten_record(rec, sep=",", explode_paths=["orders"]) 
)
write_csv(rows, "out.csv", pre_headers=["id"], header_order="stable")
```
