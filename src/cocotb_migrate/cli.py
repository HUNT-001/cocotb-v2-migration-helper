from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from cocotb_migrate.engine import migrate_file

app = typer.Typer(help="Prototype cocotb 2.x migration helper")
console = Console()


def _print_diagnostics() -> None:
    pass


@app.command()
def scan(path: Path) -> None:
    result = migrate_file(path, write=False)

    if result.changed:
        console.print(Panel.fit("[bold green]Changes detected[/bold green]"))
        console.print(result.unified_diff(str(path)) or "No diff generated.")
    else:
        console.print(Panel.fit("[bold yellow]No changes needed[/bold yellow]"))

    if result.diagnostics:
        console.print("\n[bold]Diagnostics[/bold]")
        for diag in result.diagnostics:
            style = "yellow" if diag.severity == "warning" else "cyan"
            console.print(f"[{style}]- {diag.rule}: {diag.message}[/{style}]")
    else:
        console.print("\n[bold green]No diagnostics[/bold green]")


@app.command()
def fix(path: Path) -> None:
    result = migrate_file(path, write=True)

    if result.changed:
        console.print(Panel.fit("[bold green]File updated[/bold green]"))
        console.print(result.unified_diff(str(path)) or "No diff generated.")
    else:
        console.print(Panel.fit("[bold yellow]No changes written[/bold yellow]"))

    if result.diagnostics:
        console.print("\n[bold]Diagnostics[/bold]")
        for diag in result.diagnostics:
            style = "yellow" if diag.severity == "warning" else "cyan"
            console.print(f"[{style}]- {diag.rule}: {diag.message}[/{style}]")


if __name__ == "__main__":
    app()