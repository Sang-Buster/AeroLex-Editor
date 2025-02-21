# Renamed from writers.py - handles output formatting
import json
import math
from dataclasses import dataclass
from typing import Iterator, List, TextIO

from faster_whisper.transcribe import Segment

from src.core.models import TranscribedData


def format_timestamp(seconds: float) -> str:
    """Convert seconds to timestamp format HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(",", ".")


@dataclass
class BaseFormatter:  # Renamed from ResultWriter
    result: List[TranscribedData]
    destination: str

    def write(self):
        with open(self.destination, "w", encoding="utf-8") as f:
            self._write_result(self.result, f)

    def _write_result(self, result: List[TranscribedData], file: TextIO):
        raise NotImplementedError


@dataclass
class SubtitleFormatter(BaseFormatter):  # Renamed from SubtitlesWriter
    decimal_marker: str = "."

    def iterate_result(self, result: List[TranscribedData]):
        for segment in result:
            segment_start = format_timestamp(segment["start"])
            segment_end = format_timestamp(segment["end"])
            segment_text = segment["text"].strip()
            yield segment_start, segment_end, segment_text


@dataclass
class SRTFormatter(SubtitleFormatter):  # Renamed from WriteSRT
    decimal_marker: str = ","

    def _write_result(self, result: List[TranscribedData], file: TextIO):
        for i, (start, end, text) in enumerate(self.iterate_result(result), start=1):
            print(f"{i}\n{start} --> {end}\n{text}\n", file=file, flush=True)


@dataclass
class VTTFormatter(SubtitleFormatter):  # Renamed from WriteVTT
    decimal_marker: str = "."

    def _write_result(self, result: List[TranscribedData], file: TextIO):
        print("WEBVTT\n", file=file)
        for start, end, text in self.iterate_result(result):
            print(f"{start} --> {end}\n{text}\n", file=file, flush=True)


@dataclass
class JSONFormatter(BaseFormatter):  # Renamed from WriteJSON
    def _write_result(self, result: List[TranscribedData], file: TextIO):
        json.dump(result, file)


def format_json(segments: Iterator[Segment]) -> str:
    """Format transcription as JSON with timestamps as strings"""
    result = [
        {
            "start": format_timestamp(segment.start),
            "end": format_timestamp(segment.end),
            "text": segment.text,
            "score": round(math.exp(segment.avg_logprob), 2),
            "words": [
                {
                    "start": format_timestamp(word.start),
                    "end": format_timestamp(word.end),
                    "text": word.word,
                    "score": round(word.probability, 2),
                }
                for word in (segment.words or [])
            ],
        }
        for segment in segments
    ]
    return json.dumps(result, indent=2, ensure_ascii=False)


def format_srt(segments: Iterator[Segment]) -> str:
    """Format transcription as SRT"""
    output = []
    for i, segment in enumerate(segments, start=1):
        output.extend(
            [
                str(i),
                f"{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}",
                segment.text.strip(),
                "",  # Empty line between segments
            ]
        )
    return "\n".join(output)


def format_vtt(segments: Iterator[Segment]) -> str:
    """Format transcription as WebVTT"""
    output = ["WEBVTT\n"]
    for segment in segments:
        output.extend(
            [
                f"{format_timestamp(segment.start).replace(',', '.')} --> {format_timestamp(segment.end).replace(',', '.')}",
                segment.text.strip(),
                "",  # Empty line between segments
            ]
        )
    return "\n".join(output)


FORMATTERS = {  # Renamed from WRITERS
    "json": format_json,
    "srt": format_srt,
    "vtt": format_vtt,
}
