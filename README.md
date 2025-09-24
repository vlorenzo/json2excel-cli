# JSON to Excel Converter

Convert large JSON to CSV/XLSX with root selection, flattening, array explode, exclusion, and header control.

- Advanced Usage & Troubleshooting: [docs/guide.md](docs/guide.md)
- Technical Implementation Details: [docs/tech.md](docs/tech.md)
- Quick Command Reference: [examples/commands.md](examples/commands.md)

## Features
- Streams JSON using `ijson` (no need to load entire file)
- Choose root node (dotted path or JSON Pointer)
- Flatten nested objects with a custom separator
- Options for list handling: join scalars, JSON-encode; explode specific paths into rows
- Write CSV or XLSX, with header sampling
- Control header ordering and pin selected columns to the front
- Exclude nested properties by dotted path prefix

## Installation

### For End Users
```bash
pip install json-to-excel-converter
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

### 4. Data Privacy - Remove Sensitive Information
```bash
json-to-excel-converter sample.json clean.csv --root orders --exclude customer.address --first-column order_id
```
**What you get**: Same structure but removes `customer.address.street`, `customer.address.city`, etc.

### 5. Excel Output with Custom Sheet Name
```bash
json-to-excel-converter sample.json orders.xlsx --root orders --sheet-name "Customer Orders"
```

### 6. Working with Your Own Data
Replace `sample.json` with your JSON file and adjust the `--root` path:
```bash
# For JSON with "products" array
json-to-excel-converter your-data.json output.csv --root products --first-column id

# For deeply nested data, exclude sensitive parts
json-to-excel-converter your-data.json output.csv --root items --exclude personal_info --exclude internal

# For multiple array explosions (be careful - this multiplies rows!)
json-to-excel-converter your-data.json output.csv --root orders --explode line_items --explode shipping_options
```

### Row Count Summary
- **Basic**: 3 rows (1 per order)
- **Explode items**: 6 rows (multiple items per order)
- **Explode tags**: 5 rows (different tag counts)
- **Explode both**: 12 rows (items × tags cartesian product)

## Library Usage
```python
from json_to_excel_converter.io_json import iter_items
from json_to_excel_converter.flatten import flatten_record
from json_to_excel_converter.io_table import write_csv

rows = (
    row
    for rec in iter_items("input.json", root_path="items")
    for row in flatten_record(rec, sep=".", explode_paths=["attributes"])
)
write_csv(rows, "out.csv", pre_headers=["id"], header_order="stable")
```

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
