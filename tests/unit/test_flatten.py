from __future__ import annotations

from decimal import Decimal
from json_to_excel_converter.flatten import flatten_record, ListPolicy


def test_flatten_basics_and_lists():
    record = {
        "a": {"b": 1},
        "list_scalars": [1, 2, "x"],
        "list_objs": [{"k": 1}, {"k": 2}],
        "price": Decimal("12.34"),
    }

    rows = flatten_record(record, sep=".", list_policy=ListPolicy.JOIN)
    assert isinstance(rows, list) and len(rows) == 1
    row = rows[0]

    # Dotted flatten
    assert row["a.b"] == 1

    # Scalar list join
    assert row["list_scalars"] == "1;2;x"

    # Non-scalar list defaults to JSON string
    assert isinstance(row["list_objs"], str)
    assert row["list_objs"].startswith("[") and row["list_objs"].endswith("]")

    # Decimal is preserved at this stage (writers normalize for CSV/XLSX)
    assert row["price"] == Decimal("12.34")
