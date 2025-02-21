from typing import Dict, List, TypedDict


# Data models for transcription results
class WordTiming(TypedDict):
    text: str
    start: float
    end: float
    score: float


class TranscribedData(TypedDict):
    text: str
    start: float
    end: float
    score: float
    words: List[WordTiming]


# Model configurations
MODEL_SIZES: Dict[str, int] = {
    # Standard models
    "tiny": 75,
    "small": 464,
    "medium": 1460,
    "base": 141,
    "large-v1": 2947,
    "large-v2": 2947,
    "large-v3": 2948,
    "distil-large-v2": 1446,
    "distil-large-v3": 1446,
    # English-specific models
    "tiny.en": 75,
    "small.en": 464,
    "medium.en": 1460,
    "base.en": 141,
}

MODEL_REPO_IDS = {
    # Standard models
    "tiny": "Systran/faster-whisper-tiny",
    "small": "Systran/faster-whisper-small",
    "medium": "Systran/faster-whisper-medium",
    "base": "Systran/faster-whisper-base",
    "large-v1": "Systran/faster-whisper-large-v1",
    "large-v2": "Systran/faster-whisper-large-v2",
    "large-v3": "Systran/faster-whisper-large-v3",
    "distil-large-v2": "Systran/faster-distil-whisper-large-v2",
    "distil-large-v3": "Systran/faster-distil-whisper-large-v3",
    # English-specific models
    "tiny.en": "Systran/faster-whisper-tiny.en",
    "small.en": "Systran/faster-whisper-small.en",
    "medium.en": "Systran/faster-whisper-medium.en",
    "base.en": "Systran/faster-whisper-base.en",
}

SUPPORTED_MODELS = [
    # Standard models
    "tiny",
    "small",
    "medium",
    "base",
    "large-v1",
    "large-v2",
    "large-v3",
    "distil-large-v2",
    "distil-large-v3",
    # English-specific models
    "tiny.en",
    "small.en",
    "medium.en",
    "base.en",
]
