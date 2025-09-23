# python-scripts

Python scripts for different automations

## List of Scripts

- `git-email.py`: Set the git user email address.
- `direnv-init.py`: Initialize direnv environment.

## Usage with uv

1. Allow script to be executed:
    ```bash
    chmod +x /path/to/python-scripts/git-email.py
    ```
2. Create an symbolic link. Example:
    ```bash
    ln -s /path/to/python-scripts/git-email.py ~/.local/bin/git-email
    ```
3. Verify script is installed correctly:
    ```bash
    git-email --help
    ```
