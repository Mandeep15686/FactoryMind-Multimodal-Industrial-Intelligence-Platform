"""Document loaders — PDF / DOCX / text + an OPC-UA schema loader stub.

Uses LlamaIndex's SimpleDirectoryReader when available; otherwise falls back to
plain-text reading so ingestion works in a minimal environment.
"""
from __future__ import annotations

import os
from pathlib import Path

from src.models.schemas import Document


def load_directory(path: str) -> list[Document]:
    """Load every supported file under ``path`` into Documents."""
    try:  # pragma: no cover - optional heavy dep
        from llama_index.core import SimpleDirectoryReader

        docs = SimpleDirectoryReader(path).load_data()
        return [
            Document(
                doc_id=d.doc_id or f"doc-{i}",
                text=d.text,
                metadata=dict(d.metadata or {}),
                source=str(d.metadata.get("file_path", path)),
            )
            for i, d in enumerate(docs)
        ]
    except Exception:
        return _load_plaintext(path)


def _load_plaintext(path: str) -> list[Document]:
    out: list[Document] = []
    p = Path(path)
    files = [p] if p.is_file() else list(p.rglob("*"))
    for i, f in enumerate(files):
        if f.suffix.lower() not in {".txt", ".md", ".csv", ".json"}:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        out.append(
            Document(
                doc_id=f"doc-{i}-{f.stem}",
                text=text,
                metadata={"file_name": f.name, "ext": f.suffix.lstrip(".")},
                source=str(f),
            )
        )
    return out


class OPCUASchemaLoader:
    """Loads OPC-UA node metadata into knowledge Documents (stub).

    In production this walks the OPC-UA address space via ``asyncua`` and emits a
    Document per machine describing its namespaced nodes (vibration, temperature,
    production count) for grounding sensor-analysis retrieval.
    """

    def __init__(self, endpoint: str | None = None):
        self.endpoint = endpoint or os.getenv("OPCUA_ENDPOINT", "opc.tcp://localhost:4840")

    def load(self, machine_id: str) -> list[Document]:
        return [
            Document(
                doc_id=f"opcua-{machine_id}",
                text=(
                    f"Machine {machine_id} exposes OPC-UA nodes ns=2;s=Machine.Vibration, "
                    f"ns=2;s=Machine.Temperature, ns=2;s=Machine.Pressure at {self.endpoint}."
                ),
                metadata={"machine_id": machine_id, "doc_category": "OPCUA_SCHEMA"},
                source="opcua",
            )
        ]
