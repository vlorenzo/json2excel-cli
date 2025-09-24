# JSON to Excel Converter

Convert large JSON files to CSV/XLSX with advanced data transformation features.

## Features
- Handle large JSON files efficiently
- Flatten nested objects into columns
- Convert arrays into separate rows or joined values
- Control column ordering and selection
- Support both CSV and Excel output
- Remove unwanted columns from output

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
- `--root`: path to array/object to process (optional, defaults to top-level array)
- `--explode`: create separate rows for array elements (repeatable)
- `--list-policy`: handle arrays as `join` (comma-separated) or `json` (JSON string)
- `--list-sep`: separator for joined arrays (default: ";")
- `--sample-headers`: rows to scan for column discovery (default: 1000)
- `--header-order`: column ordering `stable` (first-seen) or `alpha` (alphabetical)
- `--first-column`: pin specific columns to the beginning (repeatable)
- `--exclude`: remove columns by path prefix (repeatable)

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
```

### Row Count Summary
- **Basic**: 3 rows (1 per order)
- **Explode items**: 6 rows (multiple items per order)
- **Explode tags**: 5 rows (different tag counts)
- **Explode both**: 12 rows (items × tags cartesian product)


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
