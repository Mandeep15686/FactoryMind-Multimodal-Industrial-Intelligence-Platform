// Thin API client for the FactoryMind backend.
import type {
  Alert,
  DashboardOverview,
  MachineHealth,
  RCAReport,
} from "@shared/index";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const V1 = `${BASE}/api/v1`;

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${V1}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${V1}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return res.json();
}

export const api = {
  overview: () => get<DashboardOverview>("/dashboard/overview"),
  machines: () => get<MachineHealth[]>("/dashboard/machines"),
  alerts: () => get<Alert[]>("/alerts"),
  rca: (id: string) => get<RCAReport>(`/rca/${id}`),
  shiftReport: (shiftId: string) =>
    get<{ shift_id: string; report_markdown: string }>(`/shifts/${shiftId}/report`),
  triggerInspection: (machineId: string) =>
    post<{ id: string; jira_ticket_id: string; defect_severity: string }>("/inspections", {
      machine_id: machineId,
      triggered_by: "MANUAL",
    }),
  queryDefect: (defectId: string, question: string) =>
    post<{ answer: string }>(`/defects/${defectId}/query`, { question }),
  queryKnowledge: (query: string) =>
    post<{ documents: { doc_id: string; text: string; score: number }[] }>("/knowledge/query", {
      query,
      top_k: 5,
    }),
};

// WebSocket helper for real-time streams.
export function openStream(path: string, onMessage: (data: unknown) => void): WebSocket {
  const wsBase = BASE.replace(/^http/, "ws");
  const ws = new WebSocket(`${wsBase}${path}`);
  ws.onmessage = (e) => {
    try {
      onMessage(JSON.parse(e.data));
    } catch {
      /* ignore malformed frame */
    }
  };
  return ws;
}
