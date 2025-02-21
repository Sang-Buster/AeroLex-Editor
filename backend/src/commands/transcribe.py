import os
import subprocess
import tempfile
import time
from pathlib import Path

import click
import structlog
import torch
from faster_whisper import WhisperModel
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
)

from ..core.formatters import FORMATTERS
from .models import SUPPORTED_MODELS

MODELS_DIR = os.environ.get(
    "WSCRIBE_MODELS_DIR", os.path.expanduser("~/.cache/huggingface/hub")
)
logger = structlog.get_logger()

console = Console()


class TranscriptionProgressCallback:
    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[bold blue]{task.fields[time_info]}"),
            TextColumn("•"),
            TextColumn("Speed: {task.fields[speed]:.1f}x"),
            console=console,
            refresh_per_second=10,  # Limit refresh rate
            transient=True,  # Don't leave progress lines in terminal
        )
        self.task = None
        self.start_time = time.time()
        self.last_update = self.start_time
        self.last_duration = 0

        # Initialize task immediately
        self.task = self.progress.add_task(
            "Transcribing",
            total=100,  # Will be updated when called
            speed=0.0,
            time_info="0:00 / 0:00",
        )

    def start(self):
        """Start the progress display"""
        self.progress.start()
        return self

    def stop(self):
        """Stop the progress display"""
        self.progress.stop()

    def __call__(self, current_duration: float, total_duration: float):
        current_time = time.time()
        if current_time - self.last_update >= 0.1:  # Update every 100ms
            speed = (
                (current_duration - self.last_duration)
                / (current_time - self.last_update)
                if current_time > self.last_update
                else 0
            )

            # Format time as MM:SS
            current_mm = int(current_duration // 60)
            current_ss = int(current_duration % 60)
            total_mm = int(total_duration // 60)
            total_ss = int(total_duration % 60)
            time_info = (
                f"{current_mm:02d}:{current_ss:02d} / {total_mm:02d}:{total_ss:02d}"
            )

            self.progress.update(
                self.task,
                total=total_duration,
                completed=current_duration,
                speed=speed,
                time_info=time_info,
            )
            self.last_update = current_time
            self.last_duration = current_duration

    def __enter__(self):
        self.progress.__enter__()
        return self

    def __exit__(self, *args):
        self.progress.__exit__(*args)


def is_ffmpeg_available():
    """Check if ffmpeg is available on the system"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True)
        return True
    except FileNotFoundError:
        return False


def convert_video_to_audio(video_path: str) -> str:
    """Convert video file to temporary audio file using ffmpeg"""
    # First check if the video has an audio stream
    try:
        probe_result = subprocess.run(
            ["ffmpeg", "-i", video_path], capture_output=True, text=True
        )
        if "Stream" not in probe_result.stderr or "Audio" not in probe_result.stderr:
            click.echo("Error: No audio stream found in the video file", err=True)
            raise click.Abort()

    except subprocess.CalledProcessError as e:
        click.echo(f"Error probing video file: {e.stderr}", err=True)
        raise click.Abort()

    temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                video_path,
                "-vn",  # Disable video
                "-acodec",
                "pcm_s16le",  # Audio codec
                "-ar",
                "16000",  # Sample rate
                "-ac",
                "1",  # Mono
                "-y",  # Overwrite output file
                temp_audio.name,
            ],
            capture_output=True,
            text=True,
        )

        if not os.path.exists(temp_audio.name) or os.path.getsize(temp_audio.name) == 0:
            click.echo(
                "Error: Failed to extract audio - output file is empty", err=True
            )
            os.unlink(temp_audio.name)
            raise click.Abort()

        return temp_audio.name

    except subprocess.CalledProcessError as e:
        click.echo(f"Error converting video: {e.stderr}", err=True)
        os.unlink(temp_audio.name)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error during video conversion: {str(e)}", err=True)
        os.unlink(temp_audio.name)
        raise click.Abort()


@click.command()
@click.option(
    "-i", "--input", "input_path", required=True, help="Input audio file path"
)
@click.option(
    "-o",
    "--output",
    "output_path",
    required=True,
    help="Output transcription file path",
)
@click.option(
    "-m",
    "--model",
    "model_size",
    type=click.Choice(SUPPORTED_MODELS),
    default="medium.en",
    help="Whisper model size to use",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(list(FORMATTERS.keys())),
    default="json",
    help="Output format (json, srt, vtt)",
)
def transcribe(input_path: str, output_path: str, model_size: str, format: str):
    """Transcribe an audio file to text"""
    # Initialize temp_audio_path at the start
    temp_audio_path = None

    # Check if output file exists and handle overwriting
    if os.path.exists(output_path):
        click.echo(f"Warning: Output file '{output_path}' already exists.")
        if not click.confirm("Do you want to overwrite it?", default=True):
            click.echo("Operation cancelled - existing file was not overwritten.")
            return

    # Validate input file exists
    if not os.path.exists(input_path):
        click.echo(f"Error: Input file '{input_path}' not found", err=True)
        raise click.Abort()

    # Check ffmpeg for video files
    is_video = input_path.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".webm"))
    if is_video:
        if not is_ffmpeg_available():
            click.echo(
                "Error: ffmpeg is required for video file processing but was not found."
            )
            click.echo("Please install ffmpeg and try again.")
            raise click.Abort()
        click.echo("Video file detected, extracting audio...")
        temp_audio_path = convert_video_to_audio(input_path)
        input_path = temp_audio_path
        click.echo("Audio extraction complete.")

    # Check if model is downloaded
    model_path = (
        Path(MODELS_DIR) / f"models--Systran--faster-whisper-{model_size}" / "snapshots"
    )
    if not model_path.exists() or not any(model_path.iterdir()):
        click.echo(
            f"Error: Model '{model_size}' not found. Please download it first using:"
        )
        click.echo(f"python cli.py models download {model_size}")
        raise click.Abort()

    try:
        click.echo(f"Loading model {model_size}...")

        # Auto-detect GPU availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        click.echo(f"Using device: {device.upper()}")
        if device == "cuda":
            click.echo(f"GPU: {torch.cuda.get_device_name()}")

        # Get the actual model path from snapshots directory
        model_snapshots = list(model_path.iterdir())
        if not model_snapshots:
            click.echo(f"Error: Model snapshots not found in {model_path}")
            raise click.Abort()

        model = WhisperModel(
            model_size_or_path=str(model_snapshots[0]),
            device=device,
            compute_type=compute_type,
        )

        # Get media duration and start transcription
        click.echo(f"Analyzing {'video' if is_video else 'audio'} file...")

        try:
            # First get duration without callback
            segments, info = model.transcribe(
                input_path,
                beam_size=5,
                word_timestamps=True,
                condition_on_previous_text=True,
                initial_prompt=None,
            )

            if not info or not hasattr(info, "duration"):
                click.echo("Error: Could not determine media duration")
                raise click.Abort()

            total_duration = info.duration
            click.echo(f"\nDuration: {total_duration:.2f} seconds")
            click.echo("Starting transcription...")

            # Process segments with progress updates
            segments_list = []
            start_time = time.time()  # Move start_time here
            progress_callback = TranscriptionProgressCallback()

            with progress_callback.progress:
                for segment in segments:
                    segments_list.append(segment)
                    current_duration = segment.end
                    progress_callback(current_duration, total_duration)

            segments = segments_list  # Store processed segments

        except RuntimeError as e:
            if "Failed to load audio" in str(e):
                click.echo(
                    f"\nError: Failed to load {'video' if is_video else 'audio'} file. Please ensure ffmpeg is installed correctly."
                )
                raise click.Abort()
            raise e

        # Format and save output
        click.echo("\nFormatting output...")
        formatter = FORMATTERS[format]
        output_text = formatter(segments)

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Write output with overwrite
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)

        # Show summary
        elapsed_time = time.time() - start_time  # Use local start_time
        click.echo("\nTranscription completed!")
        click.echo(f"Media duration: {total_duration:.2f} seconds")
        click.echo(f"Processing time: {elapsed_time:.2f} seconds")
        click.echo(f"Processing speed: {total_duration / elapsed_time:.2f}x realtime")
        click.echo(f"Output saved to: {output_path}")

    except Exception as e:
        click.echo(f"\nError during transcription: {str(e)}", err=True)
        raise click.Abort()
    finally:
        # Clean up temporary audio file if it exists
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
            except Exception:
                pass
