# Renamed from transcriber.py - handles whisper model operations
from typing import List

import numpy as np
from faster_whisper import WhisperModel

from backend.core.models import TranscribedData


class WhisperEngine:  # Renamed from FasterWhisperBackend for clarity
    def __init__(
        self,
        model_size: str,
        device: str = "cpu",
        quantization: str = "int8",
        compute_type: str = "int8",
    ):
        self.model_size = model_size
        self.device = device
        self.quantization = quantization
        self.compute_type = compute_type
        self.model = None

    def load(self):
        self.model = WhisperModel(
            model_size_or_path=self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )

    def transcribe(self, input: np.ndarray) -> List[TranscribedData]:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first")

        segments, _ = self.model.transcribe(
            input,
            word_timestamps=True,
        )

        result = []
        for segment in segments:
            words = []
            for word in segment.words:
                words.append(
                    {
                        "text": word.word,
                        "start": word.start,
                        "end": word.end,
                        "score": word.probability,
                    }
                )

            result.append(
                {
                    "text": segment.text,
                    "start": segment.start,
                    "end": segment.end,
                    "score": segment.avg_logprob,
                    "words": words,
                }
            )

        return result
