"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export function DefectInspector() {
  const [defectId, setDefectId] = useState("defect-demo-1");
  const [question, setQuestion] = useState(
    "Is this crack propagating toward the weld zone?"
  );
  const [answer, setAnswer] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function ask() {
    setLoading(true);
    try {
      const res = await api.queryDefect(defectId, question);
      setAnswer(res.answer);
    } catch (e) {
      setAnswer(`Error: ${(e as Error).message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card max-w-2xl">
      <div className="mb-3 font-display text-sm font-semibold">
        Interactive Defect Inspector (VQA)
      </div>
      <input
        value={defectId}
        onChange={(e) => setDefectId(e.target.value)}
        className="mb-2 w-full rounded border border-border bg-bg px-3 py-2 text-sm"
        placeholder="Defect ID"
      />
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={3}
        className="mb-3 w-full rounded border border-border bg-bg px-3 py-2 text-sm"
      />
      <button
        onClick={ask}
        disabled={loading}
        className="rounded bg-orange px-4 py-2 text-sm font-semibold text-bg disabled:opacity-50"
      >
        {loading ? "Analyzing…" : "Ask LLaVA"}
      </button>
      {answer && (
        <div className="mt-4 rounded border-l-2 border-teal bg-teal/5 p-3 text-sm text-txt2">
          {answer}
        </div>
      )}
    </div>
  );
}
