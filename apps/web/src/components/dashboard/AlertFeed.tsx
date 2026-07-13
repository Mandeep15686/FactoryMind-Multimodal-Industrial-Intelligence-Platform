"use client";

import { useEffect, useState } from "react";
import { openStream } from "@/lib/api";
import { severityColor } from "@/lib/utils";

interface AlertFrame {
  seq: number;
  machine_id: string;
  severity: string;
  ts: string;
}

export function AlertFeed({ plantId = "plant-demo" }: { plantId?: string }) {
  const [frames, setFrames] = useState<AlertFrame[]>([]);

  useEffect(() => {
    const ws = openStream(`/ws/alerts/${plantId}`, (data) => {
      setFrames((prev) => [data as AlertFrame, ...prev].slice(0, 8));
    });
    return () => ws.close();
  }, [plantId]);

  return (
    <div className="card">
      <div className="mb-3 font-display text-sm font-semibold">Live Alert Stream</div>
      {frames.length === 0 && <div className="text-xs text-txt2">Connecting to alert stream…</div>}
      <ul className="flex flex-col gap-2">
        {frames.map((f) => (
          <li key={f.seq} className="flex items-center justify-between text-xs">
            <span className="font-mono text-txt2">{f.machine_id}</span>
            <span className={severityColor[f.severity]}>{f.severity}</span>
            <span className="text-txt2">{new Date(f.ts).toLocaleTimeString()}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
