#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["rich", "typer"]
# ///

import os
import subprocess
from typing import List

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

SOURCE_DIR = "."
TARGET_DIR = "docs"

# Create a Typer app instance and disable printing variables during exceptions
app = typer.Typer(pretty_exceptions_show_locals=False)


# Helper functions
def error_and_exit(error_message: str | None = "An error has occurred.") -> None:
    """
    Helper to output error code and exit application.
    """
    typer.secho(
        error_message,
        fg=typer.colors.RED,
    )
    raise typer.Exit(code=1)


def run_cmd(cmd: List[str]) -> None:
    """
    Helper to run commands in shell and returns stdout.
    """
    try:
        subprocess.run(cmd, text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        error_and_exit(f"Error running command: {' '.join(cmd)}")


# Main script
@app.command()
def main() -> None:
    """
    Create a new file of the script in the specified path.
    """

    file_names = []
    for entry in os.listdir(os.path.expanduser(SOURCE_DIR)):
        full_path = os.path.join(os.path.expanduser(SOURCE_DIR), entry)
        if os.path.isfile(full_path) and entry.endswith(".py"):
            file_names.append(entry[:-3])

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="[magenta]Copying files...", total=len(file_names)
        )
        for file in file_names:
            progress.console.print(f" - Copying: {file}...")
            source_path = os.path.join(SOURCE_DIR, f"{file}.py")
            target_path = os.path.join(TARGET_DIR, file)

            with open(source_path, "r") as f_source:
                content = f_source.read()

            with open(target_path, "w") as f_target:
                f_target.write(content)
            progress.advance(task)

    typer.secho(f"Files successfully created in: {TARGET_DIR}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
