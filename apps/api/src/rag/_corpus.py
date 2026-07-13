"""In-memory industrial knowledge corpus — the offline fallback used when
Qdrant / Neo4j / Elasticsearch are not reachable. Seeded from representative
maintenance knowledge so RAG works end-to-end in dev.
"""
from __future__ import annotations

from src.models.schemas import Document

CORPUS: list[Document] = [
    Document(
        doc_id="kb-001",
        text=(
            "Bearing wear on drive-end assemblies typically presents as elevated high-frequency "
            "vibration (>4 kHz) accompanied by a rising temperature trend. Root cause is often "
            "lubrication starvation or contamination ingress. Corrective action: replace bearing "
            "SKF-22222-E-C3, verify seal integrity, and re-grease to OEM torque spec of 40 Nm."
        ),
        metadata={"machine_type": "CONVEYOR", "manufacturer": "SKF", "doc_category": "RCA_REPORT", "date": "2025-11-02"},
        source="rca_history",
    ),
    Document(
        doc_id="kb-002",
        text=(
            "Elevated coolant temperature on CNC lathes correlates strongly with pump cavitation "
            "and clogged filters. When coolant exceeds 65 C the spindle bearing degradation rate "
            "roughly doubles. Inspect the coolant pump impeller and replace the 50-micron filter."
        ),
        metadata={"machine_type": "CNC_LATHE", "manufacturer": "DMG", "doc_category": "MANUAL", "date": "2025-08-14"},
        source="maintenance_manual",
    ),
    Document(
        doc_id="kb-003",
        text=(
            "Belt misalignment on presses produces a characteristic acoustic signature between "
            "800 Hz and 1.2 kHz. Left unaddressed it accelerates sheave wear. Realign using a "
            "laser alignment tool to within 0.5 mm and re-tension to 55 Nm."
        ),
        metadata={"machine_type": "PRESS", "manufacturer": "Schuler", "doc_category": "MANUAL", "date": "2025-06-30"},
        source="maintenance_manual",
    ),
    Document(
        doc_id="kb-004",
        text=(
            "Surface cracks that cross the heat-affected zone (HAZ) of a weld are classified as "
            "CRITICAL and require immediate line stop. Cracks under 0.5 mm^2 confined outside the "
            "HAZ may be monitored. Reference ISO 5817 quality level B."
        ),
        metadata={"machine_type": "WELDER", "manufacturer": "Fronius", "doc_category": "ISO_STANDARD", "date": "2024-12-01"},
        source="iso_standard",
    ),
    Document(
        doc_id="kb-005",
        text=(
            "Torque specification for bearing housing M6 bolts on the M-series conveyor drive is "
            "9.5 Nm using a calibrated torque wrench, applied in a star pattern across two passes."
        ),
        metadata={"machine_type": "CONVEYOR", "manufacturer": "SKF", "doc_category": "MANUAL", "date": "2025-03-19"},
        source="maintenance_manual",
    ),
    Document(
        doc_id="kb-006",
        text=(
            "Lubrication faults are detectable 6 to 12 hours before catastrophic bearing failure "
            "through a gradual increase in acoustic emission RMS. Automatic re-greasing systems "
            "should dispense per the OEM interval; verify the metering block is not blocked."
        ),
        metadata={"machine_type": "CONVEYOR", "manufacturer": "SKF", "doc_category": "RCA_REPORT", "date": "2025-10-22"},
        source="rca_history",
    ),
    Document(
        doc_id="kb-007",
        text=(
            "Error code E-204 on the HMI indicates a drive-end thermal trip. Confirm ambient "
            "temperature, check the cooling fan, and inspect the bearing for overheating. Persistent "
            "E-204 after reset warrants bearing replacement."
        ),
        metadata={"machine_type": "CONVEYOR", "manufacturer": "Siemens", "doc_category": "MANUAL", "date": "2025-09-05"},
        source="maintenance_manual",
    ),
    Document(
        doc_id="kb-008",
        text=(
            "Contamination defects on machined surfaces frequently trace back to coolant filtration "
            "breakdown or airborne particulate from adjacent grinding operations. Improve enclosure "
            "sealing and increase filter change frequency."
        ),
        metadata={"machine_type": "CNC_LATHE", "manufacturer": "DMG", "doc_category": "RCA_REPORT", "date": "2025-07-11"},
        source="rca_history",
    ),
    Document(
        doc_id="kb-009",
        text=(
            "Remaining Useful Life estimates below 24 hours should trigger a P0 maintenance ticket "
            "and PagerDuty escalation. RUL between 24 and 72 hours maps to P1 scheduling within the "
            "next planned downtime window."
        ),
        metadata={"machine_type": "ANY", "manufacturer": "ANY", "doc_category": "PROCEDURE", "date": "2025-01-10"},
        source="ops_procedure",
    ),
    Document(
        doc_id="kb-010",
        text=(
            "Pressure spikes on hydraulic presses combined with vibration anomalies indicate valve "
            "seat wear. Inspect the proportional valve and replace the seal kit; verify accumulator "
            "pre-charge pressure is within 10 percent of nominal."
        ),
        metadata={"machine_type": "PRESS", "manufacturer": "Bosch Rexroth", "doc_category": "MANUAL", "date": "2025-05-27"},
        source="maintenance_manual",
    ),
]
