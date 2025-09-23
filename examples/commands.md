# Example commands

```bash
. .venv/bin/activate

# Flat export from root array
json-to-excel-converter examples/ads_small.json out.csv --root items

# Explode nested list `attributes`
json-to-excel-converter examples/ads_small.json out.csv --root items --explode attributes

# Exclude a subtree and pin `id` first
json-to-excel-converter examples/ads_small.json out.xlsx --root items --exclude details --first-column id --header-order stable

# XLSX with custom sheet name
json-to-excel-converter examples/ads_small.json out.xlsx --root items --sheet-name Items
```