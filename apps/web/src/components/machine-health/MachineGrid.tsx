import type { MachineHealth } from "@shared/index";
import { healthColor } from "@/lib/utils";

export function MachineGrid({ machines }: { machines: MachineHealth[] }) {
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
      {machines.map((m) => (
        <div key={m.machine_id} className="card">
          <div className="flex items-center justify-between">
            <span className="font-mono text-sm text-txt">{m.machine_id}</span>
            <span className={`text-xs font-semibold ${healthColor[m.health_state]}`}>
              {m.health_state}
            </span>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-txt2">
            <div>RUL: {m.rul_hours}h</div>
            <div>Vibration: {m.vibration} mm/s</div>
            <div>Temp: {m.temperature_c}°C</div>
            <div>Alerts: {m.open_alerts}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
