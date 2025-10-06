#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "typer",
#     "cryptography",
# ]
# ///

from typing import List
from typing_extensions import Annotated, Literal
import typer


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


# Main script
def main(
    key_length: Annotated[
        Literal[256, 384, 2048, 4096],
        typer.Option(
            "--key-length",
            "-k",
            envvar="SCRIPT_LENGTH",
            help="Length of the key",
        ),
    ] = 256,
    validity_days: Annotated[
        int,
        typer.Option(
            "--validity-days",
            "-v",
            envvar="SCRIPT_VALIDITY",
            help="Validity period in days",
        ),
    ] = 365,
    algorithm: Annotated[
        Literal["ECDSA", "RSA"],
        typer.Option(
            "--algorithm",
            "-a",
            envvar="SCRIPT_ALGORITHM",
            help="Algorithm to use for the certificate",
            case_sensitive=False,
        ),
    ] = "ECDSA",
    country: Annotated[
        str,
        typer.Option(
            "--country-code",
            "-c",
            envvar="SCRIPT_COUNTRY",
            help="Country code for the certificate",
        ),
    ] = "DE",
    state: Annotated[
        str,
        typer.Option(
            "--state",
            "-s",
            envvar="SCRIPT_STATE",
            help="State code for the certificate",
        ),
    ] = "Bavaria",
    locality: Annotated[
        str,
        typer.Option(
            "--locality",
            "-l",
            envvar="SCRIPT_LOCALITY",
            help="Locality code for the certificate",
        ),
    ] = "Munich",
    organization: Annotated[
        str,
        typer.Option(
            "--organization",
            "-o",
            envvar="SCRIPT_ORGANIZATION",
            help="Organization name for the certificate",
        ),
    ] = "appliedAI Initiative GmbH",
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            envvar="SCRIPT_NAME",
            help="Certificate name for the certificate",
        ),
    ] = "Self-Signed Certificate",
    path: Annotated[
        str,
        typer.Option(
            "--output-path",
            "-p",
            envvar="SCRIPT_PATH",
            help="i.e.: /tmp/output",
        ),
    ] = ".",
) -> None:
    """
    Generate a self-signed SSL certificate and private key.
    """
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ec
    import datetime
    import os

    # Generate private key based on the specified algorithm
    if algorithm.upper() == "RSA":
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_length, backend=default_backend()
        )
    elif algorithm.upper() == "ECDSA":
        if key_length not in (256, 384):
            error_and_exit("Key length for ECDSA must be 256 or 384.")
        if key_length == 256:
            private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        else:
            private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
    else:
        error_and_exit("Invalid algorithm specified. Use 'RSA' or 'ECDSA'.")

    # Build a self-signed certificate
    subject = x509.Name(
        [
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, state),
            x509.NameAttribute(x509.NameOID.LOCALITY_NAME, locality),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, name),
        ]
    )

    issuer = subject  # Self-signed certificate, thus issuer is equal to subject

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
        )
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(private_key, hashes.SHA256(), default_backend())
    )

    # Get output file names
    if path == ".":
        path = os.getcwd()

    certificate_file = os.path.join(os.path.expanduser(path), "certificate.crt")
    private_key_file = os.path.join(os.path.expanduser(path), "certificate.key")

    # Write the private key to a file
    with open(private_key_file, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    # Write the certificate to a file
    with open(certificate_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    typer.echo(f"Algorithm: {algorithm}")
    typer.echo(f"Private Key: {private_key_file}")
    typer.echo(f"Certificate: {certificate_file}")

    typer.secho(
        "Self-signed SSL certificate and private key have been successfully created.",
        fg=typer.colors.GREEN,
    )


if __name__ == "__main__":
    typer.run(main)
