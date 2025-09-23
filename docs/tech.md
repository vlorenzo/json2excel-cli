## Technical Notes

### Flattening pipeline (high level)
1. Read records from the chosen root using streaming (`ijson`).
2. Flatten nested objects into dotted keys using the separator (`--sep`, default `.`).
3. Handle lists:
   - If `--explode path` is used, create one row per element at `path` (cartesian product across multiple paths).
   - Otherwise, join scalar lists with `--list-sep` when `--list-policy join` (default), or JSON-encode them when `--list-policy json`.
4. Apply exclusion: drop keys whose dotted name equals or starts with any `--exclude` prefix.
5. Build headers from a sample window (`--sample-headers`, default 1000):
   - Pin columns from `--first-column` in the given order.
   - Order remaining columns via `--header-order stable|alpha`.
6. Write rows to CSV or XLSX with type normalization (e.g., safe conversion of Decimal).

### Deterministic header behavior
- Stable order: first-seen key order across sampled rows (after pinned columns).
- Alpha: alphabetical order for non-pinned columns.
- Pinned columns always appear first (if present in the sample window).
- Columns found after the sampling window are not included; raise `--sample-headers` to capture more keys.

### List handling
- join (default): scalar lists become a single string separated by `--list-sep` (default `;`).
- json: lists become JSON strings.
- explode: rows are multiplied by the size of the exploded arrays (cartesian product when multiple `--explode` are provided).

### Types and normalization
- Scalars (str, int, float, bool, None) are preserved as-is.
- Decimal values are written as floats (fallback to string if needed) for CSV/XLSX compatibility.
- Non-serializable types in cells fall back to JSON string (or `str()` if necessary).

### Errors and messages
- Missing files: `FileNotFoundError` with the path.
- Root not found / no items: clear `ValueError` suggesting `--root` and object/array notes.
- Writers: file system errors are surfaced with their original messages.

### Known limitations
- Header sampling can miss keys appearing late in the stream; increase `--sample-headers`.
- XLSX memory footprint is higher than CSV for very large datasets.
- Exploding many arrays may produce a large cartesian product of rows.
