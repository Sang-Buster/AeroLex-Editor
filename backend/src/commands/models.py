import json
import os
import shutil
from pathlib import Path
from typing import Dict

import click
from huggingface_hub import HfApi, list_repo_refs, snapshot_download

from src.core.models import MODEL_REPO_IDS, MODEL_SIZES, SUPPORTED_MODELS

MODELS_DIR = os.environ.get(
    "WSCRIBE_MODELS_DIR", os.path.expanduser("~/.cache/huggingface/hub")
)
CUSTOM_MODELS_FILE = os.path.join(MODELS_DIR, "custom_models.json")

# Reverse mapping for full model names
REPO_TO_MODEL_ID = {v: k for k, v in MODEL_REPO_IDS.items()}


def load_custom_models() -> Dict[str, float]:
    """Load list of custom downloaded models with their sizes"""
    if os.path.exists(CUSTOM_MODELS_FILE):
        with open(CUSTOM_MODELS_FILE, "r") as f:
            data = json.load(f)
            # Handle migration from old format (list) to new format (dict)
            if isinstance(data, list):
                # Convert old list format to new dict format
                return {model: get_model_size(model) for model in data}
            return data
    return {}


def save_custom_models(models: Dict[str, float]):
    """Save list of custom downloaded models with their sizes"""
    with open(CUSTOM_MODELS_FILE, "w") as f:
        json.dump(models, f)


def get_model_size(repo_id: str) -> float:
    """Get total size of model in MB"""
    api = HfApi()
    try:
        model_info = api.model_info(repo_id=repo_id, files_metadata=True)
        total_size = sum(file.size for file in model_info.siblings if file.size)
        return round(
            total_size / (1024 * 1024), 2
        )  # Convert to MB and round to 2 decimal places
    except Exception:
        return 0


def is_valid_hf_model(repo_id: str) -> bool:
    """Check if a repository ID exists on HuggingFace"""
    api = HfApi()
    try:
        api.model_info(repo_id=repo_id)
        return True
    except Exception:
        return False


def display_model_info(repo_id: str):
    """Display detailed information about a model"""
    api = HfApi()
    try:
        model_info = api.model_info(repo_id=repo_id, files_metadata=True)

        click.echo(f"\nModel Files for {repo_id}:")
        click.echo(f"{'File':30} {'Size':>10}")
        click.echo("-" * 42)

        total_size = 0
        for file in model_info.siblings:
            if file.size:
                size_mb = file.size / (1024 * 1024)
                total_size += file.size
                click.echo(f"{file.rfilename:30} {size_mb:>10.2f} MB")

        total_size_gb = total_size / (1024 * 1024 * 1024)
        click.echo(f"\nTotal size: {total_size_gb:.2f} GB")

    except Exception as e:
        click.echo(f"Error fetching model information: {str(e)}", err=True)
        raise click.Abort()


def check_model_updates(repo_id: str) -> bool:
    """Check if there are updates available for a model
    Returns True if updates are available, False otherwise
    """
    try:
        # Get the local model path
        model_path = Path(MODELS_DIR) / repo_id.replace("/", "--") / "snapshots"
        if not model_path.exists() or not any(model_path.iterdir()):
            return False

        # Get the local revision
        local_rev = next(model_path.iterdir()).name

        # Get the latest revision from HuggingFace
        refs = list_repo_refs(repo_id)
        latest_rev = refs.main_ref.commit_id

        return local_rev != latest_rev
    except Exception as e:
        click.echo(f"Error checking updates for {repo_id}: {str(e)}", err=True)
        return False


@click.group()
def models():
    """Manage Whisper models"""
    pass


@models.command(name="list")
def list_models():
    """List all available and downloaded Whisper models"""
    click.echo("\nAvailable Whisper Models:")
    click.echo(f"{'Model':30} {'Size':>10} {'Status':>10}")
    click.echo("-" * 52)

    # List official models
    for model in SUPPORTED_MODELS:
        model_path = (
            Path(MODELS_DIR) / f"models--Systran--faster-whisper-{model}" / "snapshots"
        )
        status = (
            "Downloaded"
            if model_path.exists() and any(model_path.iterdir())
            else "Not Found"
        )
        size = f"{MODEL_SIZES[model]}MB"
        click.echo(f"{model:30} {size:>10} {status:>10}")

    # List custom downloaded models
    custom_models = load_custom_models()
    if custom_models:
        click.echo("\nCustom Downloaded Models:")
        click.echo(f"{'Model':30} {'Size':>10} {'Status':>10}")
        click.echo("-" * 52)
        for model, size in custom_models.items():
            size_str = f"{size}MB" if size else "Unknown"
            click.echo(f"{model:30} {size_str:>10} {'Downloaded':>10}")
    click.echo("")


@models.command(name="fetch")
@click.argument("repo_id")
def fetch_model(repo_id: str):
    """Fetch information about any HuggingFace model

    REPO_ID should be in the format 'organization/model-name'
    Example: Systran/faster-whisper-small
    """
    if "/" not in repo_id:
        click.echo(
            "Error: Invalid repository ID format. Should be 'organization/model-name'"
        )
        click.echo("Example: Systran/faster-whisper-small")
        raise click.Abort()

    if not is_valid_hf_model(repo_id):
        click.echo(f"Error: Model '{repo_id}' not found on HuggingFace")
        raise click.Abort()

    display_model_info(repo_id)


@models.command()
@click.argument("model_name")
def download(model_name: str):
    """Download a Whisper model

    MODEL_NAME can be either a short name (e.g., tiny, small.en) or
    full repository ID (e.g., Systran/faster-whisper-tiny)
    """
    # Handle both short and full model names
    if "/" in model_name:
        if not is_valid_hf_model(model_name):
            click.echo(f"Error: Model '{model_name}' not found on HuggingFace")
            raise click.Abort()
        repo_id = model_name
    else:
        if model_name not in MODEL_REPO_IDS:
            click.echo(f"Unknown model: {model_name}")
            return
        repo_id = MODEL_REPO_IDS[model_name]

    try:
        # Get model size before downloading
        size_mb = get_model_size(repo_id)
        if size_mb > 0:
            click.echo(f"Downloading {repo_id} (approx. {size_mb}MB)...")

        # Download the model
        snapshot_download(repo_id=repo_id)

        # If it's a custom model, add it to our custom models list with size
        if repo_id not in MODEL_REPO_IDS.values():
            custom_models = load_custom_models()
            custom_models[repo_id] = size_mb
            save_custom_models(custom_models)

        click.echo(f"Successfully downloaded model {model_name}")
    except Exception as e:
        click.echo(f"Error downloading model: {str(e)}", err=True)
        raise click.Abort()


@models.command()
@click.argument("model_name", type=click.Choice(SUPPORTED_MODELS))
def delete(model_name: str):
    """Delete a downloaded Whisper model"""
    model_path = Path(MODELS_DIR) / f"models--Systran--faster-whisper-{model_name}"

    if not model_path.exists():
        click.echo(f"Model {model_name} not found at {model_path}")
        return

    try:
        shutil.rmtree(model_path)
        click.echo(f"Successfully deleted model {model_name}")
    except Exception as e:
        click.echo(f"Error deleting model: {str(e)}", err=True)
        raise click.Abort()


@models.command()
@click.argument("model_name", required=False)
def update(model_name: str = None):
    """Update downloaded models to their latest versions

    If MODEL_NAME is provided, only that model will be updated.
    Otherwise, all downloaded models will be checked for updates.
    """
    models_to_check = []

    if model_name:
        # Handle single model update
        if "/" in model_name:
            if not is_valid_hf_model(model_name):
                click.echo(f"Error: Model '{model_name}' not found on HuggingFace")
                raise click.Abort()
            models_to_check.append((model_name, model_name))
        else:
            if model_name not in MODEL_REPO_IDS:
                click.echo(f"Unknown model: {model_name}")
                return
            models_to_check.append((model_name, MODEL_REPO_IDS[model_name]))
    else:
        # Check all downloaded models
        # First, check official models
        for model in SUPPORTED_MODELS:
            model_path = (
                Path(MODELS_DIR)
                / f"models--Systran--faster-whisper-{model}"
                / "snapshots"
            )
            if model_path.exists() and any(model_path.iterdir()):
                models_to_check.append((model, MODEL_REPO_IDS[model]))

        # Then check custom models
        custom_models = load_custom_models()
        for model in custom_models:
            models_to_check.append((model, model))

    if not models_to_check:
        click.echo("No downloaded models found to update.")
        return

    updates_available = False
    for display_name, repo_id in models_to_check:
        click.echo(f"\nChecking {display_name} for updates...")
        if check_model_updates(repo_id):
            updates_available = True
            click.echo(f"Update available for {display_name}")
            try:
                size_mb = get_model_size(repo_id)
                if size_mb > 0:
                    click.echo(
                        f"Downloading update for {repo_id} (approx. {size_mb}MB)..."
                    )

                # Force re-download the model
                snapshot_download(repo_id=repo_id, force_download=True)
                click.echo(f"Successfully updated {display_name}")
            except Exception as e:
                click.echo(f"Error updating {display_name}: {str(e)}", err=True)
        else:
            click.echo(f"{display_name} is up to date")

    if not updates_available:
        click.echo("\nAll models are up to date!")
