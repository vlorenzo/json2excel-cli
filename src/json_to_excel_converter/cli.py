from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, List, Optional

import typer
from rich.console import Console
from rich.progress import Progress

from .io_json import iter_items
from .flatten import flatten_record, ListPolicy
from .io_table import write_csv, write_xlsx

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


def _should_exclude(column: str, excludes: List[str]) -> bool:
    for p in excludes:
        if not p:
            continue
        if column == p or column.startswith(p + "."):
            return True
    return False


def _pipeline(
    input_path: Path,
    root_path: Optional[str],
    allow_object_values: bool,
    sep: str,
    list_policy: str,
    list_separator: str,
    explode: List[str],
    excludes: List[str],
) -> Iterator[dict]:
    for rec in iter_items(input_path, root_path=root_path, allow_object_values=allow_object_values):
        rows = flatten_record(
            rec,
            sep=sep,
            list_policy=list_policy,
            list_separator=list_separator,
            explode_paths=explode,
        )
        for row in rows:
            if excludes:
                filtered = {k: v for k, v in row.items() if not _should_exclude(k, excludes)}
            else:
                filtered = row
            yield filtered


@app.command()
def convert(
    input: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="Input JSON file"),
    output: Path = typer.Argument(..., help="Output file path (.csv or .xlsx)"),
    root: Optional[str] = typer.Option(None, "--root", help="Root path to iterate (dotted or JSON Pointer)"),
    allow_object_values: bool = typer.Option(False, "--allow-object-values", help="Iterate object values if root points to an object"),
    sep: str = typer.Option(".", "--sep", help="Separator for nested keys in flattened columns"),
    list_policy: str = typer.Option(ListPolicy.JOIN, "--list-policy", help="How to handle lists that are not exploded", case_sensitive=False),
    list_separator: str = typer.Option(";", "--list-sep", help="Separator for JOIN list policy"),
    explode: List[str] = typer.Option([], "--explode", help="Dotted key paths to explode into multiple rows (repeatable)", show_default=False),
    exclude: List[str] = typer.Option([], "--exclude", help="Drop columns whose dotted path equals or starts with this prefix (repeatable)", show_default=False),
    sheet_name: str = typer.Option("Sheet1", "--sheet-name", help="XLSX sheet name"),
    sample_headers: int = typer.Option(1000, "--sample-headers", help="Number of rows to sample for headers"),
    header_order: str = typer.Option("stable", "--header-order", help="Header ordering: stable or alpha", case_sensitive=False),
    first_column: List[str] = typer.Option([], "--first-column", help="Pin a column at the beginning (repeatable)"),
) -> None:
    """Convert a large JSON file into a flat table (CSV or XLSX)."""
    if output.suffix.lower() not in {".csv", ".xlsx"}:
        raise typer.BadParameter("Output must end with .csv or .xlsx")

    with Progress(transient=True) as progress:
        task = progress.add_task("Processing", start=False)
        rows = _pipeline(
            input,
            root_path=root,
            allow_object_values=allow_object_values,
            sep=sep,
            list_policy=list_policy.lower(),
            list_separator=list_separator,
            explode=explode,
            excludes=exclude,
        )

        # Wrap rows with a generator that advances a progress bar periodically
        def progress_rows() -> Iterator[dict]:
            count = 0
            progress.start_task(task)
            for r in rows:
                count += 1
                if count % 1000 == 0:
                    progress.update(task, description=f"Processed {count:,} rows")
                yield r
            progress.update(task, description=f"Processed {count:,} rows")

        pre_headers = first_column if first_column else None
        if output.suffix.lower() == ".csv":
            write_csv(
                progress_rows(),
                output,
                max_sample=sample_headers,
                pre_headers=pre_headers,
                header_order=header_order.lower(),
            )
        else:
            write_xlsx(
                progress_rows(),
                output,
                sheet_name=sheet_name,
                max_sample=sample_headers,
                pre_headers=pre_headers,
                header_order=header_order.lower(),
            )

    console.print(f"[green]Done:[/] Wrote {output}")


def main() -> None:
    app()
