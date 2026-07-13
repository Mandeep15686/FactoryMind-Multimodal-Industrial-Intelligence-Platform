import { cn } from "@/lib/utils";

export function StatCard({
  label,
  value,
  accent = "text-txt",
  sub,
}: {
  label: string;
  value: string | number;
  accent?: string;
  sub?: string;
}) {
  return (
    <div className="card">
      <div className="font-mono text-[10px] uppercase tracking-widest text-txt2">{label}</div>
      <div className={cn("mt-2 font-display text-2xl font-bold", accent)}>{value}</div>
      {sub && <div className="mt-1 text-xs text-txt2">{sub}</div>}
    </div>
  );
}
