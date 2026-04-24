import React from "react";

export default function AnalysisResult({ result }) {
  const { decision, confidence, reason, evidence, warnings, data_source } = result;
  const isBuy = decision === "BUY";
  const isSell = decision === "SELL";
  const badge = isBuy
    ? "bg-emerald-500 text-emerald-950"
    : isSell
      ? "bg-rose-500 text-rose-950"
      : "bg-slate-300 text-slate-900";

  return (
    <section className="rounded-xl bg-panel border border-line p-5 space-y-4">
      <div className="flex flex-wrap items-center gap-3 justify-between">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-md text-sm font-bold tracking-wide ${badge}`}>
            {decision}
          </span>
          <span className="text-sm text-slate-300">
            Confidence: <span className="font-semibold">{confidence}%</span>
            <span className="text-xs text-slate-500"> (capped at 85)</span>
          </span>
        </div>
        {data_source && (
          <span className="text-xs px-2 py-1 rounded bg-slate-700/60 text-slate-300 border border-line">
            Data source: {data_source}
          </span>
        )}
      </div>

      <p className="text-sm text-slate-200">{reason}</p>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Stat label="1H trend" value={evidence?.one_hour_trend} />
        <Stat label="15M structure" value={evidence?.fifteen_min_structure} />
        <Stat label="5M move" value={evidence?.five_min_move} />
        <Stat label="Image bias" value={evidence?.image_bias} />
        <Stat label="Image quality" value={evidence?.image_quality} />
        <Stat
          label="S/R zones"
          value={
            evidence?.support_resistance?.length
              ? evidence.support_resistance
                  .slice(0, 3)
                  .map((z) => `${z.type[0].toUpperCase()}: ${z.price}`)
                  .join(" · ")
              : "—"
          }
        />
      </div>

      {warnings?.length > 0 && (
        <div className="rounded-md border border-amber-400/40 bg-amber-400/10 p-3">
          <p className="text-xs uppercase tracking-wider text-amber-300 mb-1 font-semibold">
            Warnings
          </p>
          <ul className="text-sm text-amber-100 list-disc list-inside space-y-0.5">
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function Stat({ label, value }) {
  return (
    <div className="rounded-md bg-ink border border-line p-3">
      <p className="text-[11px] uppercase tracking-wider text-slate-500">{label}</p>
      <p className="text-sm font-medium text-slate-100 mt-1">{value ?? "—"}</p>
    </div>
  );
}
