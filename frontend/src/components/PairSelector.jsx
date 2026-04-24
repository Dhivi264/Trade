import React from "react";

export default function PairSelector({
  symbols,
  exchanges,
  symbol,
  exchange,
  bars,
  demo,
  onChange,
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <Field label="Pair">
        <select
          value={symbol}
          onChange={(e) => onChange({ symbol: e.target.value })}
          className="w-full bg-ink border border-line rounded-md px-3 py-2 focus:outline-none focus:border-emerald-400"
        >
          {symbols.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </Field>

      <Field label="Exchange / source">
        <select
          value={exchange}
          onChange={(e) => onChange({ exchange: e.target.value })}
          className="w-full bg-ink border border-line rounded-md px-3 py-2 focus:outline-none focus:border-emerald-400"
        >
          {exchanges.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </Field>

      <Field label="Bars per timeframe">
        <input
          type="number"
          min={60}
          max={1000}
          value={bars}
          onChange={(e) => onChange({ bars: Number(e.target.value || 0) })}
          className="w-full bg-ink border border-line rounded-md px-3 py-2 focus:outline-none focus:border-emerald-400"
        />
      </Field>

      <Field label="Demo data (no TradingView)">
        <label className="flex items-center gap-2 mt-2 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={!!demo}
            onChange={(e) => onChange({ demo: e.target.checked })}
            className="h-4 w-4 accent-emerald-500"
          />
          Use synthetic OHLC for UI testing
        </label>
      </Field>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium text-slate-400 mb-1">{label}</span>
      {children}
    </label>
  );
}
