"""HF task wrapper unit tests (mock mode)."""
from __future__ import annotations

from src.hf_tasks import (
    asr,
    audio_classification,
    ner,
    object_detection,
    sentence_similarity,
    time_series_forecast,
)


def test_object_detection_deterministic():
    a = object_detection.detect_objects("s3://x/1.jpg")
    b = object_detection.detect_objects("s3://x/1.jpg")
    assert a == b  # deterministic per input


def test_audio_classification_shape():
    r = audio_classification.classify_audio("s3://x/a.wav")
    assert {"anomaly_class", "score", "baseline_deviation"} <= set(r)


def test_ner_extracts_codes():
    ents = ner.extract_entities("Replaced part SKF-22222-E-C3 on machine M12, error E-204.")
    labels = {e.label for e in ents}
    assert "PART_NUMBER" in labels
    assert "MACHINE_ID" in labels


def test_embeddings_normalized():
    v = sentence_similarity.embed_texts(["bearing wear"])[0]
    assert abs(sum(x * x for x in v) ** 0.5 - 1.0) < 1e-6


def test_forecast_returns_health_state():
    f = time_series_forecast.forecast([50.0 + i for i in range(48)], machine_id="M12")
    assert f.health_state.value in {"HEALTHY", "DEGRADED", "CRITICAL"}


def test_asr_returns_text():
    assert isinstance(asr.transcribe("s3://x/note.wav"), str)
