# JSON to Excel / CSV CLI

[![PyPI version](https://img.shields.io/pypi/v/json-to-excel-converter)](https://pypi.org/project/json-to-excel-converter/)
[![Python versions](https://img.shields.io/pypi/pyversions/json-to-excel-converter)](https://pypi.org/project/json-to-excel-converter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A small, fast command‑line tool to convert JSON to Excel (XLSX) or CSV.
It flattens nested objects into columns and can explode arrays into multiple rows.
Input JSON is streamed from disk (via `ijson`) so you can process large files.

## Features
- Stream JSON input from disk (does not load entire file into memory)
- Flatten nested objects into dotted columns (configurable separator)
- Explode arrays into multiple rows for analysis
- Join or JSON-encode non‑exploded lists (`--list-policy join|json`)
- Discover and order headers with sampling; pin first columns
- Exclude entire column trees by prefix (e.g., `--exclude customer.address`)
- Write CSV (streaming) or Excel XLSX output (uses `openpyxl`)

## Quickstart

```bash
# Install (choose one)
pipx install json-to-excel-converter
# or
pip install json-to-excel-converter
# or, if you use uv
uv tool install json-to-excel-converter

# Convert JSON to CSV
json-to-excel-converter INPUT.json output.csv --root items --first-column id

# Convert JSON to Excel (XLSX)
json-to-excel-converter INPUT.json output.xlsx --root items --sheet-name Items
```

## Installation

### For End Users
```bash
pipx install json-to-excel-converter
# or
pip install json-to-excel-converter
# or
uv tool install json-to-excel-converter
```

### For Development
```bash
git clone https://github.com/vlorenzo/json2excel-cli
cd json2excel-cli
uv sync
. .venv/bin/activate
```

## Usage
```bash
json-to-excel-converter INPUT.json OUTPUT.(csv|xlsx) \
  --root items \
  --explode attributes \
  --list-policy join \
  --list-sep "," \
  --sep . \
  --sheet-name Items \
  --sample-headers 10 \
  --header-order stable \
  --first-column id \
  --exclude details \
  --include summary \
  --include details
```

### Options
- `--root`: path to array/object to process (optional, defaults to top-level array)
- `--explode`: create separate rows for array elements (repeatable)
- `--list-policy`: handle arrays as `join` (comma-separated) or `json` (JSON string)
- `--list-sep`: separator for joined arrays (default: ";")
- `--sample-headers`: rows to scan for column discovery (default: 1000)
- `--header-order`: column ordering `stable` (first-seen) or `alpha` (alphabetical)
- `--first-column`: pin specific columns to the beginning (repeatable)
- `--exclude`: remove columns by path prefix (repeatable)
- `--include`: keep only columns whose path equals or starts with this prefix (repeatable). Ordering of groups follows the flag order; pinned columns still appear first. Within each group, `--header-order` applies.

## FAQ

- **How do I select the part of JSON to convert?** Use `--root` with a dotted path
  like `orders.items` or a JSON Pointer like `/orders/items`. If your JSON starts
  with an array, you can omit `--root`.
- **My root is an object, not an array. What happens?** By default, the tool
  expects an array. If your root points to an object, pass `--allow-object-values`
  to iterate that object's values.
- **How do I explode arrays into rows?** Pass `--explode path` (repeatable) for each
  array you want to expand. Multiple `--explode` flags create a cartesian product
  across those arrays.
- **How are lists handled if I don't explode them?** Choose `--list-policy join`
  (default) to join scalar lists with `--list-sep` or `--list-policy json` to
  JSON‑encode the list.

## Examples

### Understanding the Sample Data
The sample contains e-commerce order data with nested structures:
```json
{
  "orders": [
    {
      "order_id": "ORD001",
      "customer": {"name": "John Smith", "address": {"city": "New York"}},
      "items": [{"product": "Laptop", "price": 1299.99}, {"product": "Mouse", "price": 29.99}],
      "payment": {"method": "credit_card", "status": "completed", "total": 1359.97},
      "tags": ["priority", "business"]
    }
    // ... 3 orders total with nested customer info, multiple items, payments, tags
  ]
}
```

### Get Sample Data
```bash
curl -O https://raw.githubusercontent.com/vlorenzo/json2excel-cli/main/sample.json
```

### 1. Basic Flattening (Nested Objects → Columns)
```bash
json-to-excel-converter sample.json orders.csv --root orders --first-column order_id
```
**What you get**: 3 rows (1 per order), nested objects become dotted columns:
- `order_id`, `customer.name`, `customer.email`, `customer.address.street`, `customer.address.city`, `payment.method`, `payment.status`, etc.
- Arrays as strings: `items` becomes JSON, `tags` becomes "priority;business"

### 2. Array Explosion - One Row Per Item Purchased
```bash
json-to-excel-converter sample.json items.csv --root orders --explode items --first-column order_id
```
**What you get**: 6 rows (one per item across all orders):
- `order_id`, `customer.name`, `items.product`, `items.brand`, `items.price`, `items.quantity`
- ORD001 creates 2 rows (Laptop + Mouse), ORD003 creates 3 rows (Keyboard + Monitor + Cable)

### 3. Multiple Array Explosions - Cartesian Product
```bash
json-to-excel-converter sample.json detailed.csv --root orders --explode items --explode tags
```
**What you get**: 12 rows (items × tags combinations)
- Every item gets a row for each tag of that order

### 4. Remove Unwanted Columns
```bash
json-to-excel-converter sample.json clean.csv --root orders --exclude customer.address --first-column order_id
```
**What you get**: Same structure but removes `customer.address.street`, `customer.address.city`, etc.

### 5. Excel Output with Custom Sheet Name
```bash
json-to-excel-converter sample.json orders.xlsx --root orders --sheet-name "Customer Orders"
```

### 6. Working with Your Own Data
Replace `sample.json` with your JSON file:
```bash
# For JSON starting with an array (no --root needed)
json-to-excel-converter your-data.json output.csv --first-column id

# For JSON with nested "products" array
json-to-excel-converter your-data.json output.csv --root products --first-column id

# Remove unwanted columns
json-to-excel-converter your-data.json output.csv --exclude personal_info --exclude internal

### 7. Include Only Certain Columns (and Order by Flag Order)
```bash
json-to-excel-converter sample.json selected.csv \
  --root orders \
  --first-column order_id \
  --include payment \
  --include customer
```
What you get: only `order_id`, then all `payment.*` columns, then all `customer.*` columns. Within each group, ordering follows `--header-order`.
```

### Row Count Summary
- **Basic**: 3 rows (1 per order)
- **Explode items**: 6 rows (multiple items per order)
- **Explode tags**: 5 rows (different tag counts)
- **Explode both**: 12 rows (items × tags cartesian product)


## When to prefer CSV over XLSX

XLSX writing is convenient but the workbook is kept in memory by `openpyxl`,
so for very large outputs CSV is usually faster and more memory‑efficient.

Consider using CSV when any of these apply:

- Your input JSON is larger than ~200 MB
- You approach Excel’s sheet limit of 1,048,576 rows

This tool streams JSON input, so it typically handles files up to around 1 GB
without issues when writing CSV.


## Contributing

### Development Setup
```bash
git clone https://github.com/vlorenzo/json2excel-cli
cd json2excel-cli
uv sync
. .venv/bin/activate
```

### Running Tests
```bash
uv run pytest -q
# Run only CLI tests
uv run pytest -q tests/cli
```

### Code Quality
```bash
uv run black .
uv run ruff check .
```
