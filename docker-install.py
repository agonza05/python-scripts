#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "typer",
#     "distro",
# ]
# ///

import subprocess
import os
import distro
import getpass
from typing import Optional
import typer


# Helper functions
def error_and_exit(error_message: Optional[str] = "An error has occurred.") -> None:
    """
    Helper to output error code and exit application.
    """
    typer.secho(
        error_message,
        fg=typer.colors.RED,
    )
    raise typer.Exit(code=1)


def check_user():
    """
    Helper to verify if script is run as root.
    """
    if os.geteuid() == 0:
        error_and_exit(
            "Do not run this script as root. The script will ask for sudo privileges."
        )


# Main script
def main() -> None:
    """
    Install docker engine in the system.
    """
    check_user()

    # Get information about the OS
    os_id = distro.id().lower()
    os_version = distro.version()

    supported_oses = {
        "ubuntu": ["24.04"],
        "debian": ["12"],
        "fedora": ["39"],
        "rhel": ["9"],
        "rocky": ["9"],
    }

    # Identify the OS and Version
    if os_id not in supported_oses:
        error_and_exit(f"Unsupported OS: {os_id}")

    if supported_oses[os_id]:
        if not any(os_version.startswith(v) for v in supported_oses[os_id]):
            error_and_exit(f"Unsupported {os_id} version: {os_version}")

    try:
        if os_id == "ubuntu" or os_id == "debian":
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(
                [
                    "sudo",
                    "apt-get",
                    "install",
                    "--no-install-recommends",
                    "-y",
                    "ca-certificates",
                    "curl",
                    "gnupg",
                ],
                check=True,
            )
            # Add Docker’s official GPG key
            subprocess.run(
                ["sudo", "install", "-m", "0755", "-d", "/etc/apt/keyrings"], check=True
            )
            subprocess.run(
                f"curl -fsSL https://download.docker.com/linux/{os_id}/gpg | "
                "sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
                shell=True,
                check=True,
            )
            subprocess.run(
                ["sudo", "chmod", "a+r", "/etc/apt/keyrings/docker.gpg"], check=True
            )
            # Set up repository
            codename = distro.codename().lower()
            repo_line = (
                f"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] "
                f"https://download.docker.com/linux/{os_id} "
                f"{codename} stable"
            )
            repo_path = "/etc/apt/sources.list.d/docker.list"
            subprocess.run(
                ["sudo", "sh", "-c", f'echo "{repo_line}" > {repo_path}'], check=True
            )
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(
                [
                    "sudo",
                    "apt-get",
                    "install",
                    "-y",
                    "docker-ce",
                    "docker-ce-cli",
                    "containerd.io",
                    "docker-buildx-plugin",
                    "docker-compose-plugin",
                ],
                check=True,
            )

        elif os_id == "fedora":
            subprocess.run(
                ["sudo", "dnf", "-y", "install", "dnf-plugins-core"], check=True
            )
            subprocess.run(
                [
                    "sudo",
                    "dnf",
                    "config-manager",
                    "--add-repo",
                    "https://download.docker.com/linux/fedora/docker-ce.repo",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "sudo",
                    "dnf",
                    "install",
                    "-y",
                    "docker-ce",
                    "docker-ce-cli",
                    "containerd.io",
                    "docker-buildx-plugin",
                    "docker-compose-plugin",
                ],
                check=True,
            )
            subprocess.run(
                ["sudo", "systemctl", "enable", "--now", "docker"], check=True
            )

        elif os_id == "rhel":
            subprocess.run(
                [
                    "sudo",
                    "yum",
                    "install",
                    "-y",
                    "yum-utils",
                    "device-mapper-persistent-data",
                    "lvm2",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "sudo",
                    "yum-config-manager",
                    "--add-repo",
                    "https://download.docker.com/linux/rhel/docker-ce.repo",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "yum",
                    "install",
                    "-y",
                    "docker-ce",
                    "docker-ce-cli",
                    "containerd.io",
                    "docker-buildx-plugin",
                    "docker-compose-plugin",
                ],
                check=True,
            )
            subprocess.run(
                ["sudo", "systemctl", "enable", "--now", "docker"], check=True
            )

        elif os_id == "rocky":
            subprocess.run(
                ["sudo", "dnf", "install", "-y", "dnf-plugins-core"], check=True
            )
            subprocess.run(
                [
                    "sudo",
                    "dnf",
                    "config-manager",
                    "--add-repo",
                    "https://download.docker.com/linux/centos/docker-ce.repo",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "sudo",
                    "dnf",
                    "install",
                    "-y",
                    "docker-ce",
                    "docker-ce-cli",
                    "containerd.io",
                    "docker-buildx-plugin",
                    "docker-compose-plugin",
                ],
                check=True,
            )
            subprocess.run(
                ["sudo", "systemctl", "enable", "--now", "docker"], check=True
            )

        # Add current user to docker group
        subprocess.run(
            ["sudo", "usermod", "-aG", "docker", getpass.getuser()], check=True
        )

    except subprocess.CalledProcessError as e:
        error_and_exit(f"Error: {e}")

    typer.secho("Docker engine successfully installed.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    typer.run(main)
