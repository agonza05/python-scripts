#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "typer",
# ]
# ///

import subprocess
from typing import List
from typing_extensions import Annotated
import typer

# Helper functions
def error_and_exit() -> None:
    """Helper to output error code and exit application."""

    typer.secho("An error has occurred.", fg=typer.colors.RED,)
    raise typer.Exit(code=1)

def run_cmd(cmd: List[str]) -> None:
    """Helper to run commands in shell and returns stdout."""

    try:
        subprocess.run(cmd, text=True, capture_output=False, check=True)
    except subprocess.CalledProcessError:
        error_and_exit()

def main(
    email: Annotated[
        str,
        typer.Option(
            "--email",
            "-e",
            envvar="EMAIL",
            help="i.e.: user@company.com",
        ),
    ] = "alberto@agonza.net",
) -> None:
    """Set the git user email address."""

    run_cmd(["git", "config", "user.email", email])
    typer.echo(f"Git user email set to: {email}")

if __name__ == "__main__":
    typer.run(main)
