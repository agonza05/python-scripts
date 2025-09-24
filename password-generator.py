#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "typer",
#     "bcrypt",
# ]
# ///

from typing import List
from typing_extensions import Annotated
import typer

# Helper functions
def error_and_exit() -> None:
    """Helper to output error code and exit application."""

    typer.secho("An error has occurred.", fg=typer.colors.RED,)
    raise typer.Exit(code=1)

# Main script
def main(
    length: Annotated[
        int,
        typer.Option(
            "--length",
            "-l",
            envvar="SCRIPT_LENGTH",
            help="Length of the password",
        ),
    ] = 32,
    # symbols: bool = False,
    symbols: Annotated[
        bool,
        typer.Option(
            "--symbols",
            "-s",
            help="Include symbols in the password",
        ),
    ] = False,
) -> None:
    """Generate a random password."""

    import secrets
    import string
    import bcrypt

    characters = string.ascii_letters + string.digits
    if symbols:
        characters += string.punctuation
    password = "".join(secrets.choice(characters) for _ in range(length))
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    if not is_valid:
        error_and_exit()
    typer.secho(f"Password: {password}", fg=typer.colors.BLUE)
    typer.secho(f"Hashed password: {hashed_password.decode('utf-8')}", fg=typer.colors.BLUE)
    typer.secho("Password generated successfully.", fg=typer.colors.GREEN)

if __name__ == "__main__":
    typer.run(main)
