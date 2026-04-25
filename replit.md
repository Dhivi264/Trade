# Chart Evidence Analyzer

Educational market-analysis tool that combines TradingView OHLC data
(1H bias, 15M structure, 5M entry) with visual inspection of an
uploaded Quotex chart screenshot. Default decision is **NO TRADE**
unless multiple independent signals align. Confidence is hard-capped
at 85; never claims guaranteed profits.

## Stack

- **Backend**: Python 3.11 + FastAPI + Uvicorn (Pandas, NumPy, OpenCV,
  Pillow). Served as the API at `/api`.
- **Frontend**: React + Vite + TypeScript + Tailwind v4 (chart-app
  artifact), served at `/`.
- **TradingView**: optional `tvdatafeed` import (unofficial / often
  blocked); falls back to CSV in `backend/data/` or a deterministic
  demo OHLC generator for UI testing.

## Layout

```
backend/                    Python FastAPI service (run by api-server artifact)
  main.py                   FastAPI entrypoint, exposes /api/*
  requirements.txt
  services/
    tv_data.py              TradingView fetch + CSV / demo fallback
    image_analysis.py       OpenCV / NumPy chart inspection
    rule_engine.py          OHLC analysis + final decision engine
  models/schemas.py         Pydantic schemas

artifacts/
  api-server/               Hosts the FastAPI service at path /api
    .replit-artifact/artifact.toml
  chart-app/                React + Vite frontend at path /
    src/
      App.tsx               Dashboard
      types.ts              Shared API types
      components/           PairSelector, UploadChart, AnalysisResult, CandleTable

frontend/                   Legacy plain-React scaffold (kept for reference)
```

## Routing & ports

- `artifacts/chart-app` (kind=web) — Vite dev server on port **22367**,
  mounted at `/`. Calls `/api/...` for backend.
- `artifacts/api-server` (kind=api) — FastAPI/Uvicorn on port **8080**,
  mounted at `/api`. The Node scaffold under `src/` is unused; the
  artifact's services run our Python backend.

## Endpoints

| Method | Path                 | Description                                  |
| ------ | -------------------- | -------------------------------------------- |
| GET    | `/api/`              | `{"status": "backend running"}`              |
| GET    | `/api/healthz`       | health probe                                 |
| GET    | `/api/ohlc`          | candles for one symbol/exchange/timeframe    |
| POST   | `/api/analyze-image` | image-only inspection                        |
| POST   | `/api/analyze`       | full multi-timeframe + image analysis        |

## Notes

- TradingView credentials are read from optional env vars
  `TV_USERNAME` and `TV_PASSWORD` only — never hardcoded.
- Uploaded images are processed in memory; nothing is persisted.
- Image type / size validated (PNG/JPG/WebP; 8 MB max).
- Confidence is capped at 85. LOW image quality further caps at 50.
- When OHLC bias / structure / image bias do not align, the engine
  returns `NO TRADE`.
