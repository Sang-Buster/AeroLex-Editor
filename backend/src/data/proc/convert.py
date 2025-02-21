import re
import json
import os
from typing import List, Dict
from dataclasses import dataclass
import random


@dataclass
class Segment:
    start: float
    end: float
    text: str


def format_timestamp(seconds: float) -> str:
    """Convert seconds to timestamp format HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(",", ".")


def parse_log_file(file_path: str) -> List[Dict]:
    segments = []
    current_segment = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # Parse header line with timestamps
            if line.startswith("{"):
                match = re.match(r"{.*?(\d+\.\d+)\s+(\d+\.\d+)}", line)
                if match:
                    start_time = float(match.group(1))
                    end_time = float(match.group(2))
                    current_segment = Segment(start_time, end_time, "")

            # Parse PUNE line
            elif line.strip().startswith("PUNE:"):
                if current_segment:
                    text = line.strip()[6:].strip()  # Remove 'PUNE: ' and whitespace
                    current_segment.text = text

                    # Create segment dictionary
                    segment_dict = {
                        "start": format_timestamp(current_segment.start),
                        "end": format_timestamp(current_segment.end),
                        "text": current_segment.text,
                        "score": 0.82,  # Default score
                        "words": [],  # We'll calculate word timings
                    }

                    # Split text into words and create approximate word timings
                    words = text.split()
                    if words:
                        word_duration = (
                            current_segment.end - current_segment.start
                        ) / len(words)
                        current_time = current_segment.start

                        for word in words:
                            word_dict = {
                                "start": format_timestamp(current_time),
                                "end": format_timestamp(current_time + word_duration),
                                "text": f" {word}",  # Add space prefix to match format
                                "score": round(
                                    random.random(), 2
                                ),  # Random score between 0 and 1
                            }
                            segment_dict["words"].append(word_dict)
                            current_time += word_duration

                    segments.append(segment_dict)
                    current_segment = None

    return segments


def convert_log_to_json(input_file: str, output_file: str) -> None:
    """
    Convert log file to JSON format

    Args:
        input_file (str): Path to input log file
        output_file (str): Path to output JSON file
    """
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Create absolute paths
    input_path = os.path.join(current_dir, input_file)
    output_path = os.path.join(current_dir, output_file)

    # Ensure input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    random.seed(42)  # For reproducible random scores

    # Convert log file to JSON format
    segments = parse_log_file(input_path)

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Write to output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    print(f"Conversion complete. Output written to {output_path}")


if __name__ == "__main__":
    convert_log_to_json("log_llm.lbs", "log.json")
