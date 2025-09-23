# python-scripts

Python scripts for different automations

## List of Scripts

- `gitemail.py`: Set the git user email address.

## Usage with uv

1. Allow script to be executed:
    ```bash
    chmod +x /path/to/python-scripts/gitemail.py
    ```
2. Create an symbolic link. Example:
    ```bash
    ln -s /path/to/python-scripts/gitemail.py ~/.local/bin/gitemail
    ```
3. Verify script is installed correctly:
    ```bash
    gitemail --help
    ```
