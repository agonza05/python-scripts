#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "rich",
#     "typer",
# ]
# ///

from typing import List
import typer


# Helper functions
def error_and_exit() -> None:
    """
    Helper to output error code and exit application.
    """
    typer.secho(
        "An error has occurred.",
        fg=typer.colors.RED,
    )
    raise typer.Exit(code=1)


def run_cmd(cmd: List[str]) -> None:
    """
    Helper to run commands in shell and returns stdout.
    """
    import subprocess

    try:
        subprocess.run(cmd, text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        error_and_exit()


# Main script
def main() -> None:
    """
    Upgrade brew packages.
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn

    brew_commands = ["update", "upgrade", "cleanup"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="[magenta]Updating packages...", total=len(brew_commands)
        )
        for command in brew_commands:
            progress.console.print(f" - brew {command}...")
            run_cmd(["brew", command])
            progress.advance(task)

    typer.secho("Packages upgraded successfully.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    typer.run(main)
