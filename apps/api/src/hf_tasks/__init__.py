"""HuggingFace inference task wrappers (15 tasks, 5 categories).

Each module exposes a primary callable with a real HF-Inference-API path and a
deterministic mock path (see ``settings.hf_use_mock``).
"""
from src.hf_tasks import (  # noqa: F401
    asr,
    audio_classification,
    document_qa,
    image_classification,
    image_feature_extraction,
    image_segmentation,
    ner,
    object_detection,
    sentence_similarity,
    summarization,
    text_ranking,
    time_series_forecast,
    visual_qa,
    zero_shot_classification,
    zero_shot_image_cls,
)

__all__ = [
    "object_detection",
    "image_segmentation",
    "image_classification",
    "image_feature_extraction",
    "zero_shot_image_cls",
    "visual_qa",
    "document_qa",
    "audio_classification",
    "asr",
    "summarization",
    "ner",
    "sentence_similarity",
    "text_ranking",
    "zero_shot_classification",
    "time_series_forecast",
]
