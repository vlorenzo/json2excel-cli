## User Guide

This guide shows how to use the converter effectively with practical examples.

### Concepts
- **Root selection (`--root`)**: Choose the array (or object) to iterate. Supports dotted paths (e.g., `items`) and JSON Pointer (e.g., `/items`).
- **Flattening**: Nested objects are flattened to dotted columns using `--sep` (default: `.`).
- **Lists**:
  - Not exploded: join scalars with `--list-sep` (default `;`) when `--list-policy join` (default), or JSON-encode with `--list-policy json`.
  - Exploded (`--explode path`): create one row per element; multiple explodes produce a cartesian product.
- **Headers**:
  - Sampled from the first N rows (`--sample-headers`, default 1000).
  - Order: pin with `--first-column`, then `--header-order stable|alpha` for the rest.
- **Exclude**: Remove columns by dotted prefix using `--exclude`.

### Quickstart
```bash
. .venv/bin/activate
json-to-excel-converter examples/ads_small.json out.csv --root items
```

### Recipes

1) Flat export from a root array
```bash
json-to-excel-converter examples/ads_small.json out.csv --root items
```

2) Explode one nested list into rows
```bash
json-to-excel-converter examples/ads_small.json out.csv \
  --root items \
  --explode attributes
```

3) Exclude a subtree and pin IDs first
```bash
json-to-excel-converter examples/ads_small.json out.xlsx \
  --root items \
  --exclude details \
  --first-column id --header-order stable
```

4) XLSX with a custom sheet name
```bash
json-to-excel-converter examples/ads_small.json out.xlsx --root items --sheet-name Items
```

### Troubleshooting
- "No items found at the given root path":
  - Verify the path (try `--root items` or `--root /items`).
  - If the top-level is an array, omit `--root`.
- Very wide or heterogeneous data:
  - Increase `--sample-headers` to include more keys in the header set.
- Decimal values and numbers:
  - Numbers are preserved; very large integers may be better exported as text for Excel readability.

### Performance tips
- Keep `--list-policy join` for readability unless you need full JSON detail.
- Use `--explode` only for the arrays you need to expand, to limit row multiplication.
- For very large files, prefer CSV over XLSX.
