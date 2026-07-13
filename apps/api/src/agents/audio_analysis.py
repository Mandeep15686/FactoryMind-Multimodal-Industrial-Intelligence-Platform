"""Audio Analysis Agent — acoustic anomaly + ASR/NER on voice notes."""
from __future__ import annotations

from src.agents.state import FactoryMindState
from src.core.observability import trace_span
from src.hf_tasks import asr, audio_classification, ner
from src.models.schemas import AudioAnomaly


def audio_analysis_node(state: FactoryMindState) -> dict:
    with trace_span("audio_analysis", machine_id=state.get("machine_id")):
        anomaly: AudioAnomaly | None = None
        for window in state.get("audio_windows", []):
            url = getattr(window, "s3_url", None) or (window.get("s3_url") if isinstance(window, dict) else None)
            if not url:
                continue
            result = audio_classification.classify_audio(url)
            if result["anomaly_class"] == "normal" and anomaly is not None:
                continue

            transcript = None
            entities = []
            # Treat non-normal windows as candidate voice notes for ASR + NER.
            if result["anomaly_class"] != "normal":
                transcript = asr.transcribe(url)
                entities = ner.extract_entities(transcript)

            candidate = AudioAnomaly(
                anomaly_class=result["anomaly_class"],
                score=result["score"],
                baseline_deviation=result["baseline_deviation"],
                transcript=transcript,
                entities=entities,
            )
            if anomaly is None or candidate.baseline_deviation > anomaly.baseline_deviation:
                anomaly = candidate

        return {"audio_anomaly": anomaly}
