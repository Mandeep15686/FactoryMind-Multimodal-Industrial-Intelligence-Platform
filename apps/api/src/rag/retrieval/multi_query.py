"""Multi-query retrieval — generate reformulations to boost recall."""
from __future__ import annotations

from src.core.config import settings


def generate_variants(query: str, n: int | None = None) -> list[str]:
    """Produce query reformulations from technical / symptom / cause angles.

    In production Claude generates these; the templated variants below keep the
    pipeline deterministic and offline-friendly while preserving the recall win.
    """
    n = n or settings.multi_query_variants
    base = query.strip().rstrip("?.")
    variants = [
        query,  # original
        f"technical specification and procedure related to {base}",  # technical paraphrase
        f"symptoms and observations indicating {base}",  # symptom-first
        f"root cause and corrective action for {base}",  # cause-first
    ]
    # de-dupe while preserving order, cap at n (+ always keep original first)
    seen: set[str] = set()
    out: list[str] = []
    for v in variants:
        key = v.lower()
        if key not in seen:
            seen.add(key)
            out.append(v)
        if len(out) >= max(n, 1):
            break
    return out
