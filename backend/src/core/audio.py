# Renamed from sources.py - handles audio processing
import numpy as np
import soundfile as sf


def decode_audio(path: str, sampling_rate: int = 16000) -> np.ndarray:
    """
    Decode audio file to numpy array
    """
    audio, sr = sf.read(path)
    # Convert stereo to mono if needed
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    # Resample if needed
    if sr != sampling_rate:
        # You may want to add resampling logic here
        pass
    return audio


class AudioLoader:  # Renamed from LocalAudio for clarity
    def __init__(self, source: str, sampling_rate: int = 16000):
        self.source_path = source
        self.sampling_rate = sampling_rate

    def load(self) -> np.ndarray:  # Renamed from convert_audio for clarity
        return decode_audio(self.source_path, self.sampling_rate)
