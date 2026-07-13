import { api } from "@/lib/api";
import { MachineGrid } from "@/components/machine-health/MachineGrid";
import { HealthChart } from "@/components/machine-health/HealthChart";
import type { MachineHealth } from "@shared/index";

const sampleTrend = Array.from({ length: 24 }, (_, i) => ({
  hour: i,
  value: Number((45 + Math.sin(i / 3) * 6 + i * 0.4).toFixed(2)),
}));

export default async function MachineHealthPage() {
  let machines: MachineHealth[] = [];
  try {
    machines = await api.machines();
  } catch {
    machines = [];
  }

  return (
    <div>
      <h1 className="mb-1 font-display text-2xl font-bold">Machine Health</h1>
      <p className="mb-6 text-sm text-txt2">
        PatchTST forecasts, RUL estimates, and live sensor trends per machine.
      </p>
      <div className="mb-6">
        <HealthChart data={sampleTrend} />
      </div>
      {machines.length > 0 ? (
        <MachineGrid machines={machines} />
      ) : (
        <div className="text-sm text-txt2">No machine data — is the API running?</div>
      )}
    </div>
  );
}
