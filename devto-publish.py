#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "typer",
#     "requests",
# ]
# ///

from pathlib import Path
from typing_extensions import Annotated
import typer
import re
import json


import requests
from typing import List, Optional


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


def validate_http_status_code(response: requests.models.Response) -> None:
    """
    Helper validate and error on http status code.
    """
    if 300 >= response.status_code < 200:
        error_and_exit("HTTP response code is not 200.")


def validate_json_key(json_key: str, response: requests.models.Response) -> None:
    """
    elper validate and error on key existence.
    """
    json_data = response.json()
    if json_key not in json_data:
        error_and_exit(f"JSON key {json_key} not found.")


# Main script
def main(
    file: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            envvar="SCRIPT_FILE",
            help="i.e.: $HOME/articles/my-post.md",
        ),
    ],
    api_token: Annotated[
        str,
        typer.Option(
            "--api-token",
            "-t",
            envvar="SCRIPT_API_TOKEN",
            help="i.e.: 1234567890abcdef1234567890abcdef",
        ),
    ],
    publish: Annotated[
        bool,
        typer.Option(
            "--publish",
            "-p",
        ),
    ] = False,
) -> None:
    """
    Publish a post to dev.to.
    """
    # Read the file
    path = Path(file)
    if not path.exists():
        error_and_exit(f"File not found: {file}")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split by --- delimiters
    parts = text.split("---", 2)
    if len(parts) < 3:
        error_and_exit("Invalid post format: missing delimiters (---)")

    # parts[0] is empty (before first ---), parts[1] is frontmatter, parts[2] is content
    frontmatter = parts[1].strip()
    content = parts[2].strip()

    # Convert publish var
    if publish:
        publish_str = "true"
    else:
        publish_str = "false"

    # Parse frontmatter
    result = {
        "title": None,
        "description": None,
        "date": None,
        "tags": [],
        "content": content,
        "publish": publish_str,
    }

    # Extract title
    title_match = re.search(r"^title:\s*(.+)$", frontmatter, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Extract description
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if desc_match:
        result["description"] = desc_match.group(1).strip()

    # Extract date
    date_match = re.search(r"^date:\s*(.+)$", frontmatter, re.MULTILINE)
    if date_match:
        result["date"] = date_match.group(1).strip()

    # Extract tags (handles format: [tag1, tag2, tag3])
    tags_match = re.search(r"^tags:\s*\[(.+?)\]", frontmatter, re.MULTILINE)
    if tags_match:
        tags_str = tags_match.group(1)
        # Split by comma and clean up each tag
        result["tags"] = [tag.strip() for tag in tags_str.split(",")]

    # # Extract tags (handles format: [tag1, tag2, tag3])
    # tags_match = re.search(r"^tags:\s*\[(.+?)\]", frontmatter, re.MULTILINE)
    # if tags_match:
    #     tags_str = tags_match.group(1)
    #     # Split by comma, trim whitespace, and keep only purely alphanumeric tags
    #     result["tags"] = [
    #         tag
    #         for tag in (t.strip() for t in tags_str.split(","))
    #         if tag and re.fullmatch(r"[A-Za-z0-9]+", tag)
    #     ]
    # else:
    #     result["tags"] = []

    # Create post data
    data = {
        "article": {
            "title": result["title"],
            "body_markdown": result["content"],
            "published": result["publish"],
            "tags": result["tags"],
        }
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": api_token,
    }

    try:
        response = requests.post(
            "https://dev.to/api/articles", json=data, headers=headers
        )
        validate_http_status_code(response)
        validate_json_key("path", response)
        json_data = response.json()
        if not json_data["path"]:
            error_and_exit("HTTP request failed.")
    except OSError:
        error_and_exit("HTTP request could not be completed.")

    typer.secho(
        f"Post published at https://dev.to{json_data['path']}",
        fg=typer.colors.BLUE,
    )
    typer.secho(
        "Post published successfully.",
        fg=typer.colors.GREEN,
    )


if __name__ == "__main__":
    typer.run(main)
