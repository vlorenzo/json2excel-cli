# Quick Reference

This file contains copy-paste commands for quick testing. For complete documentation, see the main [README.md](../README.md).

## Test Commands

```bash
# Get sample data
curl -O https://raw.githubusercontent.com/vlorenzo/json2excel-cli/main/sample.json

# Basic flattening
json-to-excel-converter sample.json orders.csv --root orders --first-column order_id

# Item explosion
json-to-excel-converter sample.json items.csv --root orders --explode items --first-column order_id

# Privacy (exclude addresses)
json-to-excel-converter sample.json clean.csv --root orders --exclude customer.address --first-column order_id

# Excel with custom sheet
json-to-excel-converter sample.json orders.xlsx --root orders --sheet-name "Orders"

# Include selected columns and order groups
json-to-excel-converter sample.json selected.csv \
  --root orders \
  --first-column order_id \
  --include payment \
  --include customer
```

## Development Examples (using sample data)
```bash
# Clone and setup for development
git clone https://github.com/vlorenzo/json2excel-cli
cd json2excel-cli
uv sync
. .venv/bin/activate

# Use included sample data
json-to-excel-converter examples/ads_small.json out.csv --root items
json-to-excel-converter examples/ads_small.json out.xlsx --root items --explode attributes
```