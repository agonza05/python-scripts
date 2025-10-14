#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "typer",
#     "requests",
# ]
# ///

from typing_extensions import Annotated
from typing import Any
import typer
import requests
from datetime import datetime, timedelta


PERSONIO_BASE_URL = "https://api.personio.de/v2"


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


def run_cmd(cmd: list[str]) -> None:
    """
    Helper to run commands in shell and returns stdout.
    """
    import subprocess

    try:
        subprocess.run(cmd, text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        error_and_exit()


def validate_http_status_code(response: requests.models.Response) -> None:
    """
    Helper validate and error on http status code.
    """
    if 300 >= response.status_code < 200:
        error_and_exit("HTTP response code is not 200.")


def validate_json_key(json_key: str, json_data: Any) -> None:
    """
    elper validate and error on key existence.
    """
    if json_key not in json_data:
        error_and_exit(f"JSON key {json_key} not found.")


def get_auth_token(client_id: str, client_secret: str) -> str:
    """
    Helper function to get auth token from Personio API.
    """
    return_data = ""
    endpoint_url = PERSONIO_BASE_URL + "/auth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.post(endpoint_url, data=payload, headers=headers)
        validate_http_status_code(response)
        json_data = response.json()
        validate_json_key("access_token", json_data)
        return_data = json_data["access_token"]
    except requests.exceptions.RequestException as e:
        error_and_exit(f"API request error. {e.strerror}")
    return return_data


def get_working_days_for_next_four_weeks(start_date: str, weeks: int) -> list[str]:
    """
    Return the working days for the following 4 weeks starting from the previous Monday.
    """
    req_date = datetime.strptime(start_date, "%Y-%m-%d")
    # Find the previous Monday
    last_monday = req_date - timedelta(days=req_date.weekday())

    # Generate working days for the next 4 weeks
    working_days = []
    for week in range(weeks):
        week_start = last_monday + timedelta(weeks=week)
        for day in range(5):  # Monday to Friday
            work_day = week_start + timedelta(days=day)
            working_days.append(work_day.strftime("%Y-%m-%d"))

    return working_days


def create_personio_attendance(
    access_token: str, employee_id: str, start_date: str
) -> None:
    """
    Helper function to create a single-day attendance.
    """
    DEFAULT_START_TIME = {
        "MORNING": "08:30:00",
        "AFTERNOON": "13:00:00",
    }
    DEFAULT_END_TIME = {
        "MORNING": "12:30:00",
        "AFTERNOON": "17:00:00",
    }

    endpoint_url = PERSONIO_BASE_URL + "/attendance-periods?skip_approval=true"
    headers = {
        "accept": "application/json",
        "Beta": "true",
        "content-type": "application/json",
        "authorization": "Bearer " + access_token,
    }
    for item in list(DEFAULT_START_TIME.keys()):
        payload = {
            "person": {"id": employee_id},
            "type": "WORK",
            "start": {"date_time": start_date + "T" + DEFAULT_START_TIME[item]},
            "end": {"date_time": start_date + "T" + DEFAULT_END_TIME[item]},
        }
        response = requests.post(endpoint_url, headers=headers, json=payload)
        validate_http_status_code(response)


# Main script
def main(
    client_id: Annotated[
        str,
        typer.Option(
            "--client-id",
            "-c",
            envvar="SCRIPT_CLIENT_ID",
            prompt="API client_id",
            help="i.e.: papi-baaaaaad-c0de-fade-baad-00000000001d",
            hide_input=True,
        ),
    ],
    client_secret: Annotated[
        str,
        typer.Option(
            "--client-secret",
            "-p",
            envvar="SCRIPT_CLIENT_SECRET",
            prompt="API client_secret",
            help="i.e.: verY-Secret-p4ssw0rd",
            hide_input=True,
        ),
    ],
    employee_id: Annotated[
        str,
        typer.Option(
            "--employee-id",
            "-i",
            envvar="SCRIPT_EMPLOYEE_ID",
            prompt="Employee ID",
            help="i.e.: 123456",
        ),
    ],
    attendance_date: Annotated[
        str,
        typer.Option(
            "--attendance-date",
            "-d",
            envvar="SCRIPT_ATTENDANCE_DATE",
            help="i.e.: 2006-01-02",
        ),
    ] = "",
    attendance_weeks: Annotated[
        int,
        typer.Option(
            "--attendance-weeks",
            "-w",
            envvar="SCRIPT_ATTENDANCE_WEEKS",
            help="i.e.: 4",
        ),
    ] = 0,
) -> None:
    """
    Create a single-day attendance.
    """
    access_token = get_auth_token(client_id, client_secret)

    start_date = attendance_date or datetime.now().strftime("%Y-%m-%d")
    if attendance_weeks == 0:
        create_personio_attendance(access_token, employee_id, start_date)
    else:
        create_attendance_weeks = get_working_days_for_next_four_weeks(
            start_date, attendance_weeks
        )
        for i in create_attendance_weeks:
            create_personio_attendance(access_token, employee_id, i)

    typer.secho("Attendance added successfully.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    typer.run(main)
