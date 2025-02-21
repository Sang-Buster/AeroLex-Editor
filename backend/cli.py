import os

import click

from src.commands.models import models
from src.commands.shell import shell
from src.commands.transcribe import transcribe

MODELS_DIR = os.environ.get(
    "WSCRIBE_MODELS_DIR", os.path.expanduser("~/.cache/huggingface/hub")
)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """🛫🎙️ AeroLex CLI: Making Airwaves Understandable

    A powerful tool for transcribing Air Traffic Control communications
    """
    os.makedirs(MODELS_DIR, exist_ok=True)


# Add commands
cli.add_command(models)
cli.add_command(transcribe)
cli.add_command(shell)

if __name__ == "__main__":
    cli()
