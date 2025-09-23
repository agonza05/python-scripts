#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "typer",
# ]
# ///

import typer

DIRENV_FILE_CONTENT = """dotenv_if_exists
source_up_if_exists
use sourceop
"""

# Helper functions
def error_and_exit() -> None:
    """Helper to output error code and exit application."""

    typer.secho("An error has occurred.", fg=typer.colors.RED,)
    raise typer.Exit(code=1)

# Main script
def main() -> None:
    """Create a new direnv file in the current directory."""

    try:
        with open(".envrc", "w") as f:
            f.write(DIRENV_FILE_CONTENT)
    except Exception:
        error_and_exit()
    typer.secho(".envrc file created successfully.", fg=typer.colors.GREEN)

if __name__ == "__main__":
    typer.run(main)
