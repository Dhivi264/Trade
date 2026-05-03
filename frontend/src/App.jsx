import React, { useState } from "react";
import PairSelector from "./components/PairSelector.jsx";
import UploadChart from "./components/UploadChart.jsx";
import AnalysisResult from "./components/AnalysisResult.jsx";
import CandleTable from "./components/CandleTable.jsx";

const SYMBOLS = [
  "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCAD", "USDCHF",
  "EURJPY", "GBPJPY", "AUDJPY", "NZDJPY", "XAUUSD", "BTCUSD", "ETHUSD",
];
export default function App() {
  const [symbol, setSymbol] = useState("EURUSD");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const onAnalyze = async () => {
    setError(null);
    setResult(null);
    if (!imageFile) {
      setError("Please upload a Quotex chart screenshot before analyzing.");
      return;
    }
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("symbol", symbol);
      fd.append("image", imageFile);

      const res = await fetch("/api/analyze", { method: "POST", body: fd });
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error(
          res.ok ? "Backend returned invalid JSON." :
          `Backend error (${res.status}). ${text.slice(0, 200)}`
        );
      }
      if (!res.ok) {
        const detail = data?.detail || data?.message || `HTTP ${res.status}`;
        throw new Error(detail);
      }
      setResult(data);
    } catch (e) {
      setError(humanizeError(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-line bg-panel/60 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center">
              <span className="text-emerald-300 font-bold">CE</span>
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-semibold tracking-tight">
                Chart Evidence Analyzer
              </h1>
              <p className="text-xs text-slate-400">
                Educational market analysis · Quotex-style charts
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        <div className="rounded-lg border border-amber-400/30 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">
          <strong>Disclaimer:</strong> This tool provides analysis only. It does not
          guarantee profit or prediction accuracy. Default decision is{" "}
          <span className="font-semibold">NO TRADE</span> unless strong evidence aligns.
        </div>

        <section className="grid gap-6 md:grid-cols-2">
          <div className="rounded-xl bg-panel border border-line p-5 space-y-4">
            <h2 className="font-semibold text-slate-200">1. Inputs</h2>
            <PairSelector
              symbols={SYMBOLS}
              symbol={symbol}
              onChange={({ symbol: s }) => {
                if (s !== undefined) setSymbol(s);
              }}
            />
            <p className="text-xs text-slate-400">
              Timeframes used: <span className="text-slate-300">1H</span> bias ·{" "}
              <span className="text-slate-300">15M</span> structure ·{" "}
              <span className="text-slate-300">5M</span> entry confirmation.
            </p>
          </div>

          <div className="rounded-xl bg-panel border border-line p-5 space-y-4">
            <h2 className="font-semibold text-slate-200">2. Quotex screenshot</h2>
            <UploadChart
              file={imageFile}
              preview={imagePreview}
              onFile={(f, dataUrl) => {
                setImageFile(f);
                setImagePreview(dataUrl);
              }}
            />
          </div>
        </section>

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <button
            onClick={onAnalyze}
            disabled={loading}
            className="rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-600 disabled:cursor-not-allowed text-slate-950 font-semibold px-5 py-2.5 transition"
          >
            {loading ? "Analyzing…" : "Analyze chart evidence"}
          </button>
          {error && (
            <div className="text-sm text-rose-300 bg-rose-500/10 border border-rose-400/30 rounded-md px-3 py-2 sm:max-w-xl">
              {error}
            </div>
          )}
        </div>

        {result && <AnalysisResult result={result} />}
        {result?.candles_preview?.length > 0 && (
          <CandleTable candles={result.candles_preview} timeframe="5M" />
        )}

        <footer className="pt-6 pb-12 text-xs text-slate-500 space-y-1">
          <p>Limitations:</p>
          <ul className="list-disc list-inside space-y-0.5">
            <li>Market data may not match Quotex exactly.</li>
            <li>OTC Quotex charts may not match live market data at all.</li>
            <li>Screenshot analysis is visual confirmation only — not exact OHLC extraction.</li>
            <li>This system does not guarantee profit. Weak or conflicting evidence returns NO TRADE.</li>
          </ul>
        </footer>
      </main>
    </div>
  );
}

function humanizeError(e) {
  const msg = String(e?.message || e || "Unknown error");
  if (msg.toLowerCase().includes("failed to fetch")) {
    return "Could not reach the backend. Make sure the API is running.";
  }
  if (msg.toLowerCase().includes("tradingview")) {
    return "Market data fetch failed. This usually means TradingView is unreachable or the asset is temporarily unavailable.";
  }
  return msg;
}
