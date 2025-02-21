import os

import click
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..core.formatters import FORMATTERS
from .models import SUPPORTED_MODELS, models
from .transcribe import transcribe

# Initialize Rich console
console = Console()


def print_welcome():
    """Display welcome message with available commands"""
    welcome_text = """
    🛫🎙️ AeroLex CLI: Making Airwaves Understandable

    A powerful web-based editor for transcription and subtitle files with real-time audio/video sync capabilities
    """
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))


def create_command_table():
    """Create a table showing available commands and their descriptions"""
    table = Table(title="Available Commands")
    table.add_column("Command", style="cyan", justify="left")
    table.add_column("Description", style="green")
    table.add_column("Example", style="yellow")

    # Transcribe commands
    table.add_row(
        "transcribe",
        "Transcribe ATC audio/video files\n"
        + "Options:\n"
        + "-i/--input: Input file path\n"
        + "-o/--output: Output file path\n"
        + "-m/--model: Model size (default: medium.en)\n"
        + "-f/--format: Output format (default: json)",
        "transcribe -i atc.mp3 -o transcript.json -m medium.en -f json",
    )

    # Model management commands
    table.add_row("models list", "List all available ASR models", "models list")
    table.add_row(
        "models download <model>",
        "Download a model (short name or full repo ID)",
        "models download medium.en\nmodels download Systran/faster-whisper-medium",
    )
    table.add_row(
        "models update [model]",
        "Update all models or specific model",
        "models update\nmodels update medium.en",
    )
    table.add_row(
        "models delete <model>", "Remove a downloaded model", "models delete medium.en"
    )
    table.add_row(
        "models fetch <repo_id>",
        "Get info about any HF model",
        "models fetch Systran/faster-whisper-large-v3",
    )

    return table


class CommandCompleter(Completer):
    """Custom completer for shell commands"""

    def __init__(self):
        self.file_extensions = [
            "mp3",
            "wav",
            "mp4",
            "avi",
            "mov",
            "json",
            "srt",
            "vtt",
            "txt",
        ]
        self.models_subcommands = ["list", "download", "update", "delete", "fetch"]

    def get_completions(self, document, complete_event):
        text = document.text
        words = text.split()

        # Handle base commands when no command is typed yet
        if len(words) == 0 or (len(words) == 1 and not text.endswith(" ")):
            commands = ["transcribe", "models", "help", "exit"]
            for command in commands:
                if command.startswith(text):
                    yield Completion(command, start_position=-len(text))
            return

        # Handle models command completions
        if words[0] == "models":
            # If we just typed models, show subcommands
            if len(words) == 1 and text.endswith(" "):
                for subcmd in self.models_subcommands:
                    yield Completion(subcmd, start_position=0)
                return

            # If we're typing a subcommand, show matching ones
            if len(words) == 2 and not text.endswith(" "):
                for subcmd in self.models_subcommands:
                    if subcmd.startswith(words[1]):
                        yield Completion(subcmd, start_position=-len(words[1]))
                return

            # Handle model names after download/delete/update/fetch
            if len(words) == 2 and text.endswith(" "):
                if words[1] in ["download", "delete", "update", "fetch"]:
                    for model in SUPPORTED_MODELS:
                        yield Completion(model, start_position=0)
                return

            if len(words) == 3 and not text.endswith(" "):
                if words[1] in ["download", "delete", "update", "fetch"]:
                    for model in SUPPORTED_MODELS:
                        if model.startswith(words[2]):
                            yield Completion(model, start_position=-len(words[2]))
                return

        # Handle transcribe command completions
        if words[0] == "transcribe":
            # If we just typed transcribe, show flags
            if len(words) == 1 and text.endswith(" "):
                flags = [
                    "-i",
                    "--input",
                    "-o",
                    "--output",
                    "-m",
                    "--model",
                    "-f",
                    "--format",
                ]
                for flag in flags:
                    yield Completion(flag, start_position=0)
                return

            # If we're after a flag, show appropriate completions
            if len(words) >= 2:
                last_word = words[-1] if not text.endswith(" ") else ""
                prev_word = words[-2] if len(words) > 1 else ""

                # Handle file path completions after -i/--input or -o/--output
                if prev_word in ["-i", "--input", "-o", "--output"]:
                    for ext in self.file_extensions:
                        if ext.startswith(last_word):
                            yield Completion(ext, start_position=-len(last_word))
                    return

                # Handle model completions after -m/--model
                elif prev_word in ["-m", "--model"]:
                    for model in SUPPORTED_MODELS:
                        if model.startswith(last_word):
                            yield Completion(model, start_position=-len(last_word))
                    return

                # Handle format completions after -f/--format
                elif prev_word in ["-f", "--format"]:
                    for fmt in FORMATTERS.keys():
                        if fmt.startswith(last_word):
                            yield Completion(fmt, start_position=-len(last_word))
                    return

                # Show remaining flags
                used_flags = set(w for w in words if w.startswith("-"))
                remaining_flags = [
                    f
                    for f in [
                        "-i",
                        "--input",
                        "-o",
                        "--output",
                        "-m",
                        "--model",
                        "-f",
                        "--format",
                    ]
                    if f not in used_flags
                ]

                for flag in remaining_flags:
                    if flag.startswith(last_word):
                        yield Completion(flag, start_position=-len(last_word))


def interactive_transcribe(ctx):
    """Interactive transcription command with autocompletion"""
    # Setup completers
    model_completer = WordCompleter(SUPPORTED_MODELS)
    format_completer = WordCompleter(list(FORMATTERS.keys()))
    file_completer = WordCompleter(
        ["mp3", "wav", "mp4", "avi", "mov", "json", "srt", "vtt", "txt"],
        pattern=r".*\.",
    )

    # Get input file
    input_path = prompt(
        "Enter ATC audio/video file path (-i/--input): ",
        completer=file_completer,
    )
    if not os.path.exists(input_path):
        console.print(f"[red]Error: File {input_path} not found[/red]")
        return

    # Get output file
    output_path = prompt(
        "Enter output transcript path (-o/--output): ",
        completer=file_completer,
    )

    # Get model with autocompletion
    model = prompt(
        "Select ASR model (-m/--model, press Tab for options): ",
        completer=model_completer,
        default="medium.en",
    )

    # Get format with autocompletion
    format = prompt(
        "Select output format (-f/--format, press Tab for options): ",
        completer=format_completer,
        default="json",
    )

    # Run transcription
    ctx.invoke(
        transcribe,
        input_path=input_path,
        output_path=output_path,
        model_size=model,
        format=format,
    )


@click.command()
@click.pass_context
def shell(ctx):
    """Launch interactive shell for AeroLex CLI"""
    print_welcome()
    console.print(create_command_table())

    command_completer = CommandCompleter()

    while True:
        try:
            command = prompt(
                "\n[aerolex]> ",
                completer=command_completer,
            )

            if command == "exit":
                break
            elif command == "help":
                console.print(create_command_table())
            elif command.startswith("transcribe"):
                # Parse command line arguments if provided
                parts = command.split()
                if len(parts) > 1:  # Has arguments
                    try:
                        # Extract arguments
                        args = parts[1:]
                        input_path = None
                        output_path = None
                        model = "medium.en"
                        format = "json"

                        # Parse arguments
                        i = 0
                        while i < len(args):
                            if args[i] in ["-i", "--input"]:
                                if i + 1 < len(args):
                                    input_path = args[i + 1]
                                    i += 2
                                else:
                                    console.print(
                                        "[red]Error: Missing value for -i/--input[/red]"
                                    )
                                    break
                            elif args[i] in ["-o", "--output"]:
                                if i + 1 < len(args):
                                    output_path = args[i + 1]
                                    i += 2
                                else:
                                    console.print(
                                        "[red]Error: Missing value for -o/--output[/red]"
                                    )
                                    break
                            elif args[i] in ["-m", "--model"]:
                                if i + 1 < len(args):
                                    model = args[i + 1]
                                    i += 2
                                else:
                                    console.print(
                                        "[red]Error: Missing value for -m/--model[/red]"
                                    )
                                    break
                            elif args[i] in ["-f", "--format"]:
                                if i + 1 < len(args):
                                    format = args[i + 1]
                                    i += 2
                                else:
                                    console.print(
                                        "[red]Error: Missing value for -f/--format[/red]"
                                    )
                                    break
                            else:
                                i += 1

                        # Only invoke transcribe if we have all required arguments
                        if input_path and output_path:
                            try:
                                ctx.invoke(
                                    transcribe,
                                    input_path=input_path,
                                    output_path=output_path,
                                    model_size=model,
                                    format=format,
                                )
                            except Exception as e:
                                console.print(f"[red]Error: {str(e)}[/red]")
                        else:
                            if not input_path:
                                console.print(
                                    "[red]Error: Input path (-i/--input) is required[/red]"
                                )
                            if not output_path:
                                console.print(
                                    "[red]Error: Output path (-o/--output) is required[/red]"
                                )
                        continue

                    except Exception as e:
                        console.print(f"[red]Error: {str(e)}[/red]")
                        continue

                # Only fall back to interactive mode if no arguments were provided
                if len(parts) == 1:
                    interactive_transcribe(ctx)
            elif command.startswith("models"):
                # Parse the models subcommand
                parts = command.split()
                if len(parts) > 1:
                    subcommand = parts[1]
                    args = parts[2:]

                    # Get the appropriate models subcommand
                    cmd = models.get_command(ctx, subcommand)
                    if cmd:
                        # Pass the first argument as model_name for download/delete/update/fetch commands
                        if subcommand in ["download", "delete", "fetch"]:
                            if args:
                                ctx.invoke(cmd, model_name=args[0])
                            else:
                                console.print("[red]Error: Model name required[/red]")
                        else:
                            # For other commands (like list), just invoke without args
                            ctx.invoke(cmd)
                    else:
                        console.print(
                            "[red]Invalid models subcommand. Type 'help' for available commands.[/red]"
                        )
                else:
                    # Just show models help if no subcommand
                    ctx.invoke(models)
            else:
                console.print(
                    "[red]Unknown command. Type 'help' for available commands.[/red]"
                )

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

    console.print("\nGoodbye! 👋")
