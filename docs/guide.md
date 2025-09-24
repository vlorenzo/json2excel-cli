## Advanced Usage Guide

### Core Concepts

#### Root Path Selection
- **Dotted paths**: `items`, `data.records`, `response.results`
- **JSON Pointer**: `/items`, `/data/records`, `/response/results`
- **Top-level arrays**: Omit `--root` entirely if your JSON starts with an array

#### Flattening Behavior
- Nested objects become dotted column names: `customer.address.city`
- Use `--sep` to change the separator: `--sep "_"` → `customer_address_city`
- Arrays are handled based on policy (see below)

#### List Handling Policies
- **`--list-policy join`** (default): Scalar arrays become `value1;value2;value3`
- **`--list-policy json`**: Arrays become JSON strings `["value1","value2"]`
- **`--explode path`**: Creates separate rows for each array element

#### Header Management
- **Sampling**: Tool reads first `--sample-headers` rows (default: 1000) to discover all possible columns
- **Ordering**: `--header-order stable` (first-seen) vs `--header-order alpha` (alphabetical)
- **Pinning**: `--first-column id --first-column name` puts these columns first

### Troubleshooting

#### Common Errors
- **"No items found at the given root path"**:
  - Check your path: `--root items` vs `--root /items` (both should work)
  - If your JSON starts with an array `[...]`, omit `--root` entirely
  - Use `--allow-object-values` if your root points to an object instead of array

- **Missing columns in output**:
  - Increase `--sample-headers 5000` to scan more rows for column discovery
  - Some columns might appear late in the data stream

- **Too many rows after explosion**:
  - Multiple `--explode` flags create cartesian products (rows multiply)
  - Use `--explode` selectively only for arrays you need to analyze

#### Performance Optimization
- **Large files**: Prefer CSV over XLSX (faster, smaller memory footprint)
- **Wide data**: Use `--exclude prefix` to remove unnecessary column trees
- **Memory usage**: The tool streams JSON, but XLSX writing loads everything in memory
- **List handling**: Keep `--list-policy join` unless you need full JSON arrays

#### Data Quality Issues
- **Mixed data types**: Tool handles this gracefully, missing fields become empty cells
- **Large numbers**: Very large integers might display in scientific notation in Excel
- **Special characters**: UTF-8 is preserved in both CSV and XLSX output
- **Null values**: JSON `null` becomes empty cells, not the string "null"
