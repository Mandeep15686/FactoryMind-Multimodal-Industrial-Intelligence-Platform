"""Graph RAG — Neo4j multi-hop traversal with an in-memory graph fallback.

Models: (Machine)-[HAS_FAILURE_MODE]->(FailureMode)
        -[HAS_ROOT_CAUSE]->(RootCause)-[RESOLVED_BY]->(Action)
"""
from __future__ import annotations

from src.core.config import settings

# In-memory knowledge graph (fallback when Neo4j is unreachable).
_GRAPH: dict[str, dict] = {
    "CONVEYOR": {
        "bearing wear": {
            "cause": "lubrication starvation / contamination ingress",
            "action": "replace bearing SKF-22222-E-C3, verify seals, re-grease to 40 Nm",
        },
        "overheating": {
            "cause": "cooling fan failure or drive-end thermal trip (E-204)",
            "action": "inspect cooling fan; replace bearing if E-204 persists after reset",
        },
    },
    "CNC_LATHE": {
        "coolant fault": {
            "cause": "pump cavitation / clogged 50-micron filter",
            "action": "replace filter, inspect pump impeller",
        },
        "contamination": {
            "cause": "coolant filtration breakdown / airborne particulate",
            "action": "improve enclosure sealing, increase filter change frequency",
        },
    },
    "PRESS": {
        "belt misalignment": {
            "cause": "sheave wear / improper tension",
            "action": "laser-align to 0.5 mm, re-tension to 55 Nm",
        },
        "valve seat wear": {
            "cause": "hydraulic pressure spikes",
            "action": "replace proportional valve seal kit, check accumulator pre-charge",
        },
    },
}


class GraphRetriever:
    def __init__(self) -> None:
        self._driver = None
        try:  # pragma: no cover - optional service
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(
                settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
            )
            self._driver.verify_connectivity()
        except Exception:
            self._driver = None

    def traverse(self, machine_type: str | None, symptoms: list[str]) -> list[str]:
        """Return human-readable failure→cause→action paths for the symptoms."""
        if self._driver is not None:  # pragma: no cover
            try:
                return self._cypher(machine_type, symptoms)
            except Exception:
                pass
        return self._memory_traverse(machine_type, symptoms)

    def _memory_traverse(self, machine_type: str | None, symptoms: list[str]) -> list[str]:
        paths: list[str] = []
        types = [machine_type] if machine_type in _GRAPH else list(_GRAPH.keys())
        sym_l = [s.lower() for s in symptoms]
        for mt in types:
            for mode, node in _GRAPH[mt].items():
                if any(tok in mode or mode in tok for tok in sym_l) or not symptoms:
                    paths.append(
                        f"({mt})-[HAS_FAILURE_MODE]->({mode})-[HAS_ROOT_CAUSE]->"
                        f"({node['cause']})-[RESOLVED_BY]->({node['action']})"
                    )
        return paths[:5]

    def _cypher(self, machine_type: str | None, symptoms: list[str]) -> list[str]:  # pragma: no cover
        query = (
            "MATCH (m:Machine)-[:HAS_FAILURE_MODE]->(f:FailureMode)"
            "-[:HAS_ROOT_CAUSE]->(r:RootCause)-[:RESOLVED_BY]->(a:Action) "
            "WHERE ($mt IS NULL OR m.type = $mt) "
            "RETURN m.type AS mt, f.name AS mode, r.name AS cause, a.name AS action LIMIT 5"
        )
        with self._driver.session() as session:
            rows = session.run(query, mt=machine_type)
            return [
                f"({r['mt']})-[HAS_FAILURE_MODE]->({r['mode']})-[HAS_ROOT_CAUSE]->"
                f"({r['cause']})-[RESOLVED_BY]->({r['action']})"
                for r in rows
            ]
