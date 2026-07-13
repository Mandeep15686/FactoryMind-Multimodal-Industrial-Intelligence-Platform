"""Automatic Speech Recognition — Whisper-large-v3. Technician voice notes."""
from __future__ import annotations

from src.hf_tasks._client import fetch_bytes, hf_infer, is_mock, seeded_rng

MODEL = "openai/whisper-large-v3"
_SAMPLES = [
    "Machine M12 conveyor bearing sounding rough on the drive end, error code E-204 showing on the HMI.",
    "Replaced belt on press P07, part number SKF-22222-E-C3, torque checked to spec.",
    "Coolant temperature elevated on lathe M05, recommend inspecting pump before next shift.",
]


def transcribe(audio_url: str) -> str:
    """Return the transcript text for a voice note."""
    if not is_mock():
        payload = fetch_bytes(audio_url)
        if payload is not None:
            result = hf_infer(MODEL, payload, task="automatic-speech-recognition")
            if result:
                return result.get("text", "") if isinstance(result, dict) else str(result)
    rng = seeded_rng("asr:" + audio_url)
    return rng.choice(_SAMPLES)
