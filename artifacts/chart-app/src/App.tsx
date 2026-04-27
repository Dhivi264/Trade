import { useState } from "react";
import PairSelector from "./components/PairSelector";
import UploadChart from "./components/UploadChart";
import AnalysisResult from "./components/AnalysisResult";
import CandleTable from "./components/CandleTable";
import type { AnalyzeResponse, DetectResponse } from "./types";

const SYMBOLS = [
  "EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCAD", "USDCHF",
  "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY",
  "EURGBP", "EURAUD", "EURCAD", "EURCHF",
  "GBPAUD", "GBPCAD", "GBPCHF", "GBPNZD",
  "AUDCAD", "AUDCHF",
  "XAUUSD", "XAGUSD",
  "BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD",
];
const EXCHANGES = ["OANDA", "FX_IDC", "FOREXCOM", "BINANCE"];

export default function App() {
  const [autoDetect, setAutoDetect] = useState(true);
  const [symbol, setSymbol] = useState("EURUSD");
  const [exchange, setExchange] = useState("OANDA");
  const [demo, setDemo] = useState(false);
  const bars = 300;
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const [detection, setDetection] = useState<DetectResponse | null>(null);
  const [detecting, setDetecting] = useState(false);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onPickFile = async (f: File, dataUrl: string) => {
    setImageFile(f);
    setImagePreview(dataUrl);
    setDetection(null);
    setResult(null);
    setError(null);
    if (!autoDetect) return;
    setDetecting(true);
    try {
      const fd = new FormData();
      fd.append("image", f);
      const res = await fetch("/api/detect-from-image", {
        method: "POST",
        body: fd,
      });
      const data: DetectResponse = await res.json();
      setDetection(data);
      if (data.symbol) {
        setSymbol(data.symbol);
        if (data.exchange) setExchange(data.exchange);
      }
    } catch (e) {
      setDetection({
        symbol: null,
        exchange: null,
        is_otc: false,
        raw_text: "",
        confidence: 0,
        candidates: [],
        reason: humanizeError(e),
      });
    } finally {
      setDetecting(false);
    }
  };

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
      // When auto-detect is ON, send no symbol/exchange so the backend
      // OCRs the image and decides. When OFF, send the manual choices.
      if (!autoDetect) {
        fd.append("symbol", symbol);
        fd.append("exchange", exchange);
      } else if (detection?.symbol) {
        // We already detected — send what we showed the user so the
        // result matches what they see on screen.
        fd.append("symbol", detection.symbol);
        if (detection.exchange) fd.append("exchange", detection.exchange);
      }
      fd.append("bars", String(bars));
      fd.append("demo", String(demo));
      fd.append("image", imageFile);

      const res = await fetch("/api/analyze", { method: "POST", body: fd });
      const text = await res.text();
      let data: AnalyzeResponse | { detail?: string; message?: string };
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error(
          res.ok
            ? "Backend returned invalid JSON."
            : `Backend error (${res.status}). ${text.slice(0, 200)}`,
        );
      }
      if (!res.ok) {
        const detail =
          (data as { detail?: string; message?: string }).detail ||
          (data as { detail?: string; message?: string }).message ||
          `HTTP ${res.status}`;
        throw new Error(detail);
      }
      setResult(data as AnalyzeResponse);
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

        <section className="rounded-xl bg-panel border border-line p-5 space-y-4">
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <div>
              <h2 className="font-semibold text-slate-200">1. Upload Quotex screenshot</h2>
              <p className="text-xs text-slate-400 mt-1">
                Drop a screenshot of your Quotex chart. The pair name is auto-detected
                from the image.
              </p>
            </div>
            <label className="flex items-center gap-2 text-xs text-slate-300 select-none">
              <input
                type="checkbox"
                checked={autoDetect}
                onChange={(e) => {
                  setAutoDetect(e.target.checked);
                  if (e.target.checked && imageFile) {
                    void onPickFile(imageFile, imagePreview ?? "");
                  }
                }}
                className="h-4 w-4 accent-emerald-500"
              />
              Auto-detect pair from image
            </label>
          </div>

          <UploadChart
            file={imageFile}
            preview={imagePreview}
            onFile={onPickFile}
          />

          {autoDetect && (
            <DetectionPanel detecting={detecting} detection={detection} />
          )}
        </section>

        {!autoDetect && (
          <section className="rounded-xl bg-panel border border-line p-5 space-y-4">
            <h2 className="font-semibold text-slate-200">2. Manual inputs</h2>
            <PairSelector
              symbols={SYMBOLS}
              exchanges={EXCHANGES}
              symbol={symbol}
              exchange={exchange}
              demo={demo}
              onChange={({ symbol: s, exchange: e, demo: d }) => {
                if (s !== undefined) setSymbol(s);
                if (e !== undefined) setExchange(e);
                if (d !== undefined) setDemo(d);
              }}
            />
            <p className="text-xs text-slate-400">
              Timeframes used: <span className="text-slate-300">1H</span> bias ·{" "}
              <span className="text-slate-300">15M</span> structure ·{" "}
              <span className="text-slate-300">5M</span> entry confirmation.
            </p>
          </section>
        )}

        {autoDetect && (
          <section className="rounded-xl bg-panel border border-line px-5 py-3">
            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={demo}
                onChange={(e) => setDemo(e.target.checked)}
                className="h-4 w-4 accent-emerald-500"
              />
              Use synthetic OHLC for UI testing
            </label>
          </section>
        )}

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <button
            onClick={onAnalyze}
            disabled={loading || (autoDetect && (detecting || !detection?.symbol))}
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
        {result?.candles_preview && result.candles_preview.length > 0 && (
          <CandleTable candles={result.candles_preview} timeframe="5M" />
        )}

        <footer className="pt-6 pb-12 text-xs text-slate-500 space-y-1">
          <p>Limitations:</p>
          <ul className="list-disc list-inside space-y-0.5">
            <li>TradingView data may not match Quotex exactly.</li>
            <li>OTC Quotex charts may not match TradingView data at all.</li>
            <li>Screenshot analysis is visual confirmation only — not exact OHLC extraction.</li>
            <li>This system does not guarantee profit. Weak or conflicting evidence returns NO TRADE.</li>
          </ul>
        </footer>
      </main>
    </div>
  );
}

function DetectionPanel({
  detecting,
  detection,
}: {
  detecting: boolean;
  detection: DetectResponse | null;
}) {
  if (detecting) {
    return (
      <div className="rounded-md bg-ink border border-line px-3 py-2 text-sm text-slate-300 flex items-center gap-2">
        <span className="inline-block h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
        Reading pair name from screenshot…
      </div>
    );
  }
  if (!detection) {
    return (
      <div className="rounded-md bg-ink border border-line px-3 py-2 text-sm text-slate-400">
        Pair will be detected automatically once you upload a screenshot.
      </div>
    );
  }
  if (!detection.symbol) {
    return (
      <div className="rounded-md border border-amber-400/40 bg-amber-400/10 px-3 py-2 text-sm text-amber-100">
        <p className="font-medium">Could not detect a pair from this screenshot.</p>
        <p className="text-xs mt-1 text-amber-200/80">
          {detection.reason || "Try a clearer screenshot, or turn off auto-detect to pick manually."}
        </p>
      </div>
    );
  }
  return (
    <div className="rounded-md border border-emerald-400/30 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-100">
      <div className="flex flex-wrap items-center gap-2">
        <span className="px-2 py-0.5 rounded bg-emerald-400/20 border border-emerald-400/40 font-semibold tracking-wide">
          {detection.symbol}
        </span>
        {detection.is_otc && (
          <span className="px-2 py-0.5 rounded bg-amber-400/20 border border-amber-400/40 text-amber-100 text-xs font-semibold">
            OTC
          </span>
        )}
        <span className="text-xs text-emerald-200/80">
          via {detection.exchange ?? "—"} · OCR confidence {detection.confidence}%
        </span>
      </div>
      {detection.is_otc && (
        <p className="text-xs mt-1 text-amber-100">
          Quotex OTC asset — TradingView data may not match exactly.
        </p>
      )}
    </div>
  );
}

function humanizeError(e: unknown): string {
  const msg = String((e as Error)?.message || e || "Unknown error");
  if (msg.toLowerCase().includes("failed to fetch")) {
    return "Could not reach the backend. Make sure the API is running.";
  }
  if (msg.toLowerCase().includes("tradingview")) {
    return msg + "  (Tip: enable Demo data to test the UI without TradingView.)";
  }
  return msg;
}
