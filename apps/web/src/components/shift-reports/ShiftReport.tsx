import { api } from "@/lib/api";

export async function ShiftReport({ shiftId = "shift-demo" }: { shiftId?: string }) {
  let markdown = "";
  try {
    const res = await api.shiftReport(shiftId);
    markdown = res.report_markdown;
  } catch (e) {
    markdown = `Failed to load report: ${(e as Error).message}`;
  }

  return (
    <div className="card max-w-3xl">
      <div className="mb-3 font-display text-sm font-semibold">
        Shift Handover Report — {shiftId}
      </div>
      <pre className="whitespace-pre-wrap text-sm leading-relaxed text-txt2">{markdown}</pre>
    </div>
  );
}
