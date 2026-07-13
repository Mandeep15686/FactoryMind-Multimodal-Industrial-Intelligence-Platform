import { api } from "@/lib/api";
import { StatCard } from "@/components/dashboard/StatCard";
import { AlertFeed } from "@/components/dashboard/AlertFeed";
import type { DashboardOverview } from "@shared/index";

async function getOverview(): Promise<DashboardOverview | null> {
  try {
    return await api.overview();
  } catch {
    return null;
  }
}

export default async function DashboardPage() {
  const o = await getOverview();

  return (
    <div>
      <h1 className="mb-1 font-display text-2xl font-bold">Plant Overview</h1>
      <p className="mb-6 text-sm text-txt2">
        Real-time multimodal health across the production line.
      </p>

      {o ? (
        <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4">
          <StatCard label="Machines" value={o.machines_total} />
          <StatCard label="Critical" value={o.machines_critical} accent="text-red" />
          <StatCard label="Open Alerts" value={o.open_alerts} accent="text-orange" />
          <StatCard
            label="Avg RCA Conf."
            value={`${Math.round(o.avg_rca_confidence * 100)}%`}
            accent="text-teal"
          />
        </div>
      ) : (
        <div className="mb-6 rounded border-l-2 border-yellow bg-yellow/5 p-3 text-sm text-txt2">
          Backend unreachable — start the API with <code>make dev</code>.
        </div>
      )}

      <AlertFeed />
    </div>
  );
}
