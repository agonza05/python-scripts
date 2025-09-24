#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "typer",
# ]
# ///

from typing import List
from typing_extensions import Annotated
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
def main(
    email: Annotated[
        str,
        typer.Option(
            "--email",
            "-e",
            envvar="SCRIPT_EMAIL",
            help="i.e.: user@company.com",
        ),
    ] = "alberto@agonza.net",
) -> None:
    """
    Set the git user email address.
    """
    run_cmd(["git", "config", "user.email", email])
    typer.secho(f"Git user email successfully set to: {email}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    typer.run(main)
