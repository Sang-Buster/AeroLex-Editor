import json
import re


def parse_log_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    # Pattern to match each log entry block
    pattern = r"\{(log_id_\d+\s+\d+\s+log_id_\d+__([^_]+)__([^_]+)__(\d+_\d+_\d+)\s+(\d+\.\d+)\s+(\d+\.\d+))\}(.*?)(?=\{log_id_|\Z)"

    entries = []

    for match in re.finditer(pattern, content, re.DOTALL):
        speaker = match.group(2)
        listener = match.group(3)
        start_time = float(match.group(5))
        end_time = float(match.group(6))
        block_content = match.group(7)

        # Extract PUNE line
        pune_match = re.search(r"PUNE:\s*(.*?)(?:\r?\n)", block_content)
        if pune_match:
            pune_text = pune_match.group(1).strip()

            # Format timestamps
            start_formatted = format_timestamp(start_time)
            end_formatted = format_timestamp(end_time)

            entry = {
                "start": start_formatted,
                "end": end_formatted,
                "text": pune_text,
                "speaker": speaker,
                "listener": listener,
            }

            entries.append(entry)

    return entries


def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS.### format"""
    total_milliseconds = int(seconds * 1000)
    hours = total_milliseconds // 3600000
    minutes = (total_milliseconds % 3600000) // 60000
    seconds = (total_milliseconds % 60000) / 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def main():
    # Replace with your actual file path
    file_path = "log_llm.lbs"

    entries = parse_log_file(file_path)

    # Write to JSON file
    with open("log.json", "w") as outfile:
        json.dump(entries, outfile, indent=4)

    print(f"Extracted {len(entries)} entries to output.json")


if __name__ == "__main__":
    main()
