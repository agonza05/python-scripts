#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "jinja2",
#     "typer",
#     "pyyaml",
# ]
# ///

from typing_extensions import Annotated
import typer


# Main script
def main(
    template_path: Annotated[
        str,
        typer.Option(
            "--template-path",
            "-t",
            envvar="SCRIPT_TEMPLATE",
            help="i.e.: /tmp/template.yml.j2",
        ),
    ] = "template.j2",
    data_path: Annotated[
        str,
        typer.Option(
            "--data-path",
            "-d",
            envvar="SCRIPT_DATA",
            help="i.e.: /tmp/data.yml",
        ),
    ] = "data.yml",
    output_path: Annotated[
        str,
        typer.Option(
            "--output-path",
            "-o",
            envvar="SCRIPT_OUTPUT",
            help="i.e.: /tmp/output.yml",
        ),
    ] = "output.yml",
) -> None:
    """
    Generate output file from template.
    """
    import os
    import yaml
    from jinja2 import Environment, FileSystemLoader

    # Setup Jinja and load the template
    template_dir = os.path.dirname(template_path) or "."
    template_file = os.path.basename(template_path)
    env = Environment(loader=FileSystemLoader(template_dir))
    jinja_template = env.get_template(template_file)

    # Load YAML data
    with open(data_path) as f:
        vars_data = yaml.safe_load(f)

    # Render template
    rendered = jinja_template.render(**vars_data)

    # Write to output file
    with open(output_path, "w") as f:
        f.write(rendered)

    typer.secho(
        f"Template rendered successfully. Output file: {output_path}",
        fg=typer.colors.GREEN,
    )


if __name__ == "__main__":
    typer.run(main)
