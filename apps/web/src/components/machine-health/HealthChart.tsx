"use client";

import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function HealthChart({ data }: { data: { hour: number; value: number }[] }) {
  return (
    <div className="card h-64">
      <div className="mb-2 font-display text-sm font-semibold">Vibration Trend (7d)</div>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data}>
          <XAxis dataKey="hour" stroke="#8A97B4" fontSize={10} />
          <YAxis stroke="#8A97B4" fontSize={10} />
          <Tooltip
            contentStyle={{ background: "#0F1219", border: "1px solid #1C2133", fontSize: 12 }}
          />
          <Line type="monotone" dataKey="value" stroke="#FF5F1F" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
