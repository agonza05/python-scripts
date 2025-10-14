#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "typer",
#     "requests",
# ]
# ///

from typing_extensions import Annotated, Literal
import typer
import requests


DNS_BASE_URL = "https://api.cloudflare.com/client/v4"


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


def value_callback(value: str) -> str:
    """
    Gets the public ip address of the host system.
    """
    if value == "":
        import requests

        value = requests.get("https://checkip.amazonaws.com").text.strip()
    return value


# Main script
def main(
    fqdn: Annotated[
        str,
        typer.Option(
            "--fqdn",
            "-f",
            envvar="SCRIPT_FQDN",
            help="i.e.: www.example.com",
        ),
    ],
    zone_id: Annotated[
        str,
        typer.Option(
            "--zone-id",
            "-z",
            envvar="SCRIPT_ZONE_ID",
            help="i.e.: 1234567890abcdef1234567890abcdef",
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
    value: Annotated[
        str,
        typer.Option(
            "--value",
            "-v",
            envvar="SCRIPT_VALUE",
            help="i.e.: 192.168.1.1",
            callback=value_callback,
        ),
    ] = "",
    record_type: Annotated[
        Literal["A", "CNAME"],
        typer.Option(
            "--record-type",
            "-r",
            envvar="SCRIPT_RECORD_TYPE",
            help="i.e.: A",
            case_sensitive=False,
        ),
    ] = "A",
) -> None:
    """
    Update a DNS record.
    """
    record_id = record_content = ""
    endpoint_url = DNS_BASE_URL + f"/zones/{zone_id}/dns_records"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_token,
    }
    params = {
        "name": fqdn,
        "type": record_type,
    }
    try:
        response = requests.get(url=endpoint_url, headers=headers, params=params)
        validate_http_status_code(response)
        validate_json_key("success", response)
        json_data = response.json()
        if json_data["success"] and json_data["result_info"]["count"] == 1:
            record_id = json_data["result"][0]["id"]
            record_content = json_data["result"][0]["content"]
        else:
            error_and_exit("DNS API call failed.")
    except OSError:
        error_and_exit("DNS API call could not be completed.")

    if record_content == value:
        typer.secho(
            "DNS record already matches the current IP address.", fg=typer.colors.YELLOW
        )
    else:
        typer.secho(
            f"DNS record does not match the current IP address. Updating {record_type} record for {fqdn} with {value}.",
            fg=typer.colors.YELLOW,
        )
        endpoint_url = DNS_BASE_URL + f"/zones/{zone_id}/dns_records/{record_id}"
        payload = {"content": value}
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_token,
        }
        try:
            response = requests.patch(url=endpoint_url, json=payload, headers=headers)
            validate_http_status_code(response)
            validate_json_key("success", response)
            json_data = response.json()
            if not json_data["success"]:
                error_and_exit("DNS API call failed.")
        except OSError:
            error_and_exit("DNS API call could not be completed.")

    typer.secho("DNS record updated successfully.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    typer.run(main)
