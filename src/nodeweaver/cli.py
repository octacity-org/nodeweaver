"""Command-line interface: `nodeweaver <command>`."""

from pathlib import Path

import typer

from nodeweaver.discovery import find_python_files

app = typer.Typer(add_completion=False)


# With a single command, Typer would turn the app into that command
# (`nodeweaver PATH` instead of `nodeweaver scan PATH`). A callback keeps
# `scan` a subcommand, so more commands can be added later.
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Turn a codebase into an interactive architecture map."""
    # `nodeweaver` with no command shows the help and exits with code 0.
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def scan(
    path: Path = typer.Argument(..., metavar="PATH", help="Directory to scan."),
) -> None:
    """List the Python files in PATH, relative to PATH and sorted.

    Skips .git, .venv, venv, __pycache__, node_modules, .pytest_cache,
    .mypy_cache, build and dist.
    """
    # Checked here instead of with typer.Argument(exists=True), which would
    # exit with code 2. The issue asks for exit code 1.
    if not path.exists():
        typer.echo(f"Error: path does not exist: {path}", err=True)
        raise typer.Exit(code=1)
    if not path.is_dir():
        typer.echo(f"Error: not a directory: {path}", err=True)
        raise typer.Exit(code=1)

    files = find_python_files(path)
    if not files:
        typer.echo(f"No Python files found in {path}", err=True)
        return
    for file in files:
        typer.echo(file)
