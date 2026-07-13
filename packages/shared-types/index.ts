// Shared TypeScript types mirroring the backend Pydantic schemas.
// Keep in sync with apps/api/src/models/schemas.py.

export type Severity = "CRITICAL" | "MAJOR" | "MINOR" | "NONE";
export type HealthState = "HEALTHY" | "DEGRADED" | "CRITICAL";
export type Priority = "P0" | "P1" | "P2" | "P3";
export type DefectType =
  | "CRACK"
  | "SCRATCH"
  | "CONTAMINATION"
  | "MISALIGNMENT"
  | "UNKNOWN";

export interface BoundingBox {
  x: number;
  y: number;
  w: number;
  h: number;
  image_url?: string;
}

export interface Defect {
  defect_type: DefectType;
  severity: Severity;
  confidence: number;
  bbox?: BoundingBox;
  area_mm2?: number;
  description?: string;
}

export interface MachineHealth {
  machine_id: string;
  health_state: HealthState;
  rul_hours: number;
  vibration: number;
  temperature_c: number;
  open_alerts: number;
}

export interface Alert {
  id: string;
  plant_id: string;
  machine_id: string;
  severity: Severity;
  status: "OPEN" | "ACKNOWLEDGED" | "RESOLVED";
  rca_id?: string;
}

export interface RCAReport {
  id: string;
  machine_id: string;
  hypothesis: string;
  root_causes: string[];
  recommendations: string[];
  confidence: number;
  retrieved_docs: string[];
  engineer_verdict?: "CORRECT" | "PARTIAL" | "WRONG";
}

export interface DashboardOverview {
  plant_id: string;
  machines_total: number;
  machines_healthy: number;
  machines_degraded: number;
  machines_critical: number;
  open_alerts: number;
  open_tickets: number;
  defect_rate_24h: number;
  avg_rca_confidence: number;
}
