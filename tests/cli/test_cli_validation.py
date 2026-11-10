from __future__ import annotations

from pathlib import Path
from typer.testing import CliRunner
from json_to_excel_converter.cli import app


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_invalid_list_policy_rejected(tmp_path: Path):
    runner = CliRunner()
    src = project_root() / "examples" / "ads_small.json"
    dst = tmp_path / "out.csv"

    result = runner.invoke(app, [str(src), str(dst), "--root", "items", "--list-policy", "bogus"])
    assert result.exit_code == 2, result.output
    assert not dst.exists()


def test_invalid_header_order_rejected(tmp_path: Path):
    runner = CliRunner()
    src = project_root() / "examples" / "ads_small.json"
    dst = tmp_path / "out.csv"

    result = runner.invoke(app, [str(src), str(dst), "--root", "items", "--header-order", "bogus"])
    assert result.exit_code == 2, result.output
    assert not dst.exists()
