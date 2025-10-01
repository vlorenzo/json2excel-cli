from __future__ import annotations

from pathlib import Path
from typer.testing import CliRunner
from json_to_excel_converter.cli import app


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_csv_basic(tmp_path: Path):
    runner = CliRunner()
    src = project_root() / "examples" / "ads_small.json"
    dst = tmp_path / "out.csv"

    result = runner.invoke(app, [str(src), str(dst), "--root", "items", "--first-column", "id"])
    assert result.exit_code == 0, result.output
    assert dst.exists()

    header = dst.read_text(encoding="utf-8").splitlines()[0]
    cols = header.split(",")
    assert cols[0] == "id"
    # Expect some flattened column from summary
    assert any(c.startswith("summary.") for c in cols)


def test_csv_exclude(tmp_path: Path):
    runner = CliRunner()
    src = project_root() / "examples" / "ads_small.json"
    dst = tmp_path / "out.csv"

    result = runner.invoke(app, [str(src), str(dst), "--root", "items", "--exclude", "details"])
    assert result.exit_code == 0, result.output

    header = dst.read_text(encoding="utf-8").splitlines()[0]
    cols = header.split(",")
    assert not any(c.startswith("details.") for c in cols)


def test_csv_include_and_order(tmp_path: Path):
    runner = CliRunner()
    src = project_root() / "examples" / "ads_small.json"
    dst = tmp_path / "out.csv"

    # Include summary first, then details; pin id first
    result = runner.invoke(
        app,
        [
            str(src),
            str(dst),
            "--root",
            "items",
            "--first-column",
            "id",
            "--include",
            "summary",
            "--include",
            "details",
        ],
    )
    assert result.exit_code == 0, result.output
    header = dst.read_text(encoding="utf-8").splitlines()[0]
    cols = header.split(",")
    # id must be first
    assert cols[0] == "id"
    # All columns should be from summary.* or details.* (and id)
    assert all(c == "id" or c.startswith("summary.") or c.startswith("details.") for c in cols)
    # The first non-pinned column should come from the first include prefix (summary)
    assert cols[1].startswith("summary.")


def test_csv_include_and_exclude(tmp_path: Path):
    runner = CliRunner()
    src = project_root() / "examples" / "ads_small.json"
    dst = tmp_path / "out.csv"

    result = runner.invoke(
        app,
        [
            str(src),
            str(dst),
            "--root",
            "items",
            "--include",
            "summary",
            "--exclude",
            "summary.internal",
        ],
    )
    assert result.exit_code == 0, result.output
    header = dst.read_text(encoding="utf-8").splitlines()[0]
    cols = header.split(",")
    # No details.* columns should be present
    assert not any(c.startswith("details.") for c in cols)
    # Exclusion of a subset under summary should be respected
    assert not any(c.startswith("summary.internal") for c in cols)
