#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "rich",
#     "typer",
# ]
# ///

from typing import List
from typing_extensions import Annotated
import typer

TARGET_PATH = "~/.local/bin"


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
def main(
    path: Annotated[
        str,
        typer.Option(
            "--path",
            "-p",
            envvar="SCRIPT_PATH",
            help="i.e.: $HOME/python-scripts",
        ),
    ] = ".",
) -> None:
    """
    Create a symbolic link to the script in the specified path.
    """
    import os
    from rich.progress import Progress, SpinnerColumn, TextColumn

    if path == ".":
        path = os.getcwd()
    file_names = []
    for entry in os.listdir(os.path.expanduser(path)):
        full_path = os.path.join(os.path.expanduser(path), entry)
        if os.path.isfile(full_path) and entry.endswith(".py"):
            file_names.append(entry[:-3])

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="[magenta]Creating symlinks...", total=len(file_names)
        )
        for file in file_names:
            progress.console.print(f" - Link for: {file}...")
            run_cmd(["chmod", "+x", f"{path}/{file}.py"])
            run_cmd(
                [
                    "ln",
                    "-sf",
                    f"{path}/{file}.py",
                    os.path.expanduser(f"{TARGET_PATH}/{file}"),
                ]
            )
            progress.advance(task)

    typer.secho(
        f"Symlinks successfully created in: {TARGET_PATH}", fg=typer.colors.GREEN
    )


if __name__ == "__main__":
    typer.run(main)
