from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence

import orjson
from openpyxl import Workbook
from decimal import Decimal


def _collect_headers(
    rows: Iterable[Dict[str, object]],
    max_sample: int = 1000,
    pre_headers: Sequence[str] | None = None,
    order: str = "stable",
) -> tuple[List[str], List[Dict[str, object]], Iterator[Dict[str, object]]]:
    """
    Look ahead up to max_sample rows to build a header list and return
    a generator that yields first the buffered rows then the rest.

    order:
    - "stable": preserve first-seen key order across sampled rows
    - "alpha": alphabetical after pre_headers
    """
    pre_headers = list(pre_headers or [])
    buffer: List[Dict[str, object]] = []

    it = iter(rows)
    for _ in range(max_sample):
        try:
            row = next(it)
        except StopIteration:
            break
        buffer.append(row)

    if order == "alpha":
        header_set: set[str] = set(pre_headers)
        for r in buffer:
            header_set.update(r.keys())
        headers = pre_headers + sorted(h for h in header_set if h not in pre_headers)
    else:
        seen: set[str] = set(pre_headers)
        headers: List[str] = list(pre_headers)
        for r in buffer:
            for k in r.keys():
                if k not in seen:
                    seen.add(k)
                    headers.append(k)

    def chained() -> Iterator[Dict[str, object]]:
        for r in buffer:
            yield r
        for r in it:
            yield r

    return headers, buffer, chained()


def _normalize_cell(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        # Keep numeric type when possible, but avoid Decimal serialization issues
        try:
            return float(value)
        except Exception:
            return str(value)
    if isinstance(value, (str, int, float, bool)):
        return value
    # Fallback: JSON string
    try:
        return orjson.dumps(value).decode("utf-8")
    except TypeError:
        return str(value)


def write_csv(
    rows: Iterable[Dict[str, object]],
    output_file: str | Path,
    *,
    include_headers: bool = True,
    max_sample: int = 1000,
    pre_headers: Sequence[str] | None = None,
    encoding: str = "utf-8",
    header_order: str = "stable",
) -> None:
    import csv

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    headers, _buf, chained = _collect_headers(
        rows, max_sample=max_sample, pre_headers=pre_headers, order=header_order
    )

    with out_path.open("w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        if include_headers:
            writer.writeheader()
        for row in chained:
            normalized = {k: _normalize_cell(row.get(k)) for k in headers}
            writer.writerow(normalized)


def write_xlsx(
    rows: Iterable[Dict[str, object]],
    output_file: str | Path,
    *,
    sheet_name: str = "Sheet1",
    include_headers: bool = True,
    max_sample: int = 1000,
    pre_headers: Sequence[str] | None = None,
    header_order: str = "stable",
) -> None:
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    headers, _buf, chained = _collect_headers(
        rows, max_sample=max_sample, pre_headers=pre_headers, order=header_order
    )

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    row_idx = 1
    if include_headers:
        ws.append(headers)
        row_idx += 1

    for row in chained:
        ws.append([_normalize_cell(row.get(k)) for k in headers])
        row_idx += 1

    wb.save(out_path)
