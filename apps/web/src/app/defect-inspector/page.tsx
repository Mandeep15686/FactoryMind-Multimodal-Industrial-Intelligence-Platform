import { DefectInspector } from "@/components/defect-inspector/DefectInspector";

export default function DefectInspectorPage() {
  return (
    <div>
      <h1 className="mb-1 font-display text-2xl font-bold">Defect Inspector</h1>
      <p className="mb-6 text-sm text-txt2">
        Ask natural-language questions about a defect image — powered by LLaVA VQA.
      </p>
      <DefectInspector />
    </div>
  );
}
