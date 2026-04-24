# Chart Evidence Analyzer

Educational market-analysis tool that combines TradingView OHLC data
(1H bias, 15M structure, 5M entry) with visual inspection of an
uploaded Quotex chart screenshot. Default decision is **NO TRADE**
unless multiple independent signals align. Confidence is hard-capped
at 85; never claims guaranteed profits.

## Stack

- **Backend**: Python 3.11 + FastAPI + Uvicorn (Pandas, NumPy, OpenCV,
  Pillow). Single process serves both the API and the built React app.
- **Frontend**: React 18 + Vite + Tailwind CSS, built to
  `frontend/dist/` and served by FastAPI in production.
- **TradingView**: optional `tvdatafeed` import (unofficial / often
  blocked); falls back to CSV in `backend/data/` or a deterministic
  demo OHLC generator for UI testing.

## Layout

```
backend/
  main.py                 FastAPI entrypoint, mounts /api/* and SPA fallback
  requirements.txt
  services/
    tv_data.py            TradingView fetch + CSV / demo fallback
    image_analysis.py     OpenCV / NumPy chart inspection
    rule_engine.py        OHLC analysis + final decision engine
  models/schemas.py       Pydantic schemas

frontend/
  src/App.jsx             Dashboard
  src/components/         PairSelector, UploadChart, AnalysisResult, CandleTable
  vite.config.js          dev proxy /api -> :8080, builds to dist/
```

## Workflow & port

- The `artifacts/api-server` artifact runs `uvicorn` (Python) on port
  **8080** and is mounted at path **`/`**. FastAPI serves both the
  React build and the API.
- Production build runs `cd frontend && npm install && npm run build`
  before booting uvicorn.
- The Node Express scaffold under `artifacts/api-server/src/` is
  unused — the artifact's services run our Python backend.

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
