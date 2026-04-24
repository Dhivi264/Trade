import React from "react";

export default function CandleTable({ candles, timeframe }) {
  if (!candles?.length) return null;
  return (
    <section className="rounded-xl bg-panel border border-line p-5 space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-slate-200">
          Latest {candles.length} candles
        </h2>
        <span className="text-xs text-slate-400">Timeframe: {timeframe}</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-400 text-xs uppercase tracking-wider">
            <tr>
              <th className="py-2 pr-3">Time</th>
              <th className="py-2 pr-3">Open</th>
              <th className="py-2 pr-3">High</th>
              <th className="py-2 pr-3">Low</th>
              <th className="py-2 pr-3">Close</th>
              <th className="py-2 pr-3">Δ</th>
            </tr>
          </thead>
          <tbody>
            {candles.map((c, i) => {
              const up = c.close >= c.open;
              return (
                <tr key={i} className="border-t border-line/60">
                  <td className="py-1.5 pr-3 text-slate-400 whitespace-nowrap">
                    {formatTime(c.time)}
                  </td>
                  <td className="py-1.5 pr-3">{c.open}</td>
                  <td className="py-1.5 pr-3">{c.high}</td>
                  <td className="py-1.5 pr-3">{c.low}</td>
                  <td className="py-1.5 pr-3">{c.close}</td>
                  <td
                    className={`py-1.5 pr-3 font-medium ${
                      up ? "text-emerald-300" : "text-rose-300"
                    }`}
                  >
                    {(c.close - c.open).toFixed(5)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function formatTime(t) {
  try {
    const d = new Date(t);
    if (isNaN(d.getTime())) return t;
    return d.toISOString().replace("T", " ").slice(0, 16);
  } catch {
    return t;
  }
}
