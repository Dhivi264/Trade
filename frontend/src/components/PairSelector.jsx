import React from "react";

export default function PairSelector({
  symbols,
  symbol,
  onChange,
}) {
  return (
    <div className="space-y-4">
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
