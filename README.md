# Chart Evidence Analyzer

Educational market-analysis tool for Quotex-style binary trading charts. It
combines TradingView OHLC data (1H bias, 15M structure, 5M entry) with a
visual inspection of an uploaded Quotex screenshot, then runs a strict
rule engine that defaults to **NO TRADE** unless multiple independent
signals align.

> ⚠️ This tool provides analysis only. It does NOT guarantee profit or
> prediction accuracy and never auto-trades.

## Project layout

```
backend/                  Python FastAPI service
  main.py                 API entrypoint and SPA static-serving
  requirements.txt
  services/
    tv_data.py            TradingView fetch (tvdatafeed) + CSV / demo fallback
    image_analysis.py     OpenCV / NumPy chart screenshot inspection
    rule_engine.py        OHLC analysis + final decision engine
  models/
    schemas.py            Pydantic schemas

frontend/                 React + Vite + Tailwind dashboard
  src/
    App.jsx
    main.jsx
    components/
      UploadChart.jsx
      AnalysisResult.jsx
      PairSelector.jsx
      CandleTable.jsx
```

## Local setup

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

The API is now available at `http://localhost:8080/api/`.

### 2. Frontend (dev)

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

The Vite dev server proxies `/api` to FastAPI on port 8080.

### 3. Production build (single-server)

```bash
cd frontend && npm install && npm run build
cd ../backend && uvicorn main:app --host 0.0.0.0 --port 8080
```

FastAPI now serves both the API and the compiled React app from
`frontend/dist`. One Replit URL exposes the whole product.

## Replit hosting

This project is wired into the existing Replit workflow so you can:

- Open the preview pane to use the running app (FastAPI serves the built
  React dashboard at `/` and the API at `/api/...`).
- Restart the backend workflow after changing Python code.
- Re-run `npm run build` inside `frontend/` after changing the UI.

## TradingView data

`backend/services/tv_data.py` does:

1. **Try `tvdatafeed`** — uses optional env vars `TV_USERNAME` /
   `TV_PASSWORD` if you have them. The library is unofficial and is
   often blocked by TradingView; failures are caught.
2. **Try CSV fallback** — drop files at
   `backend/data/<EXCHANGE>_<SYMBOL>_<TIMEFRAME>.csv` with columns
   `time,open,high,low,close,volume`.
3. **Demo mode** — when the user toggles "Demo data" the API generates
   a deterministic synthetic OHLC series. This is for UI testing only
   and the response is clearly marked `data_source: "synthetic"`.

If nothing works the API returns a clear 502:

```
TradingView data fetch failed. Check symbol/exchange/timeframe or use CSV fallback.
```

## Why "NO TRADE" is common

The decision engine is intentionally strict. It will return BUY or SELL
only when **all** of the following align:

- 1H trend matches direction (BULLISH or BEARISH — not RANGE/UNCLEAR)
- 15M structure agrees
- 5M shows BUY_PRESSURE / SELL_PRESSURE
- Uploaded screenshot's visual bias does not disagree
- Image quality is at least MEDIUM
- The market is not overextended on the 5M
- Price is not stuck mid-range

Otherwise the response is **NO TRADE** with a reason and warnings.
Confidence is hard-capped at 85, image-quality LOW caps it at 50, and
no scenario ever returns 90%+.

## Endpoints

| Method | Path                | Description                                  |
| ------ | ------------------- | -------------------------------------------- |
| GET    | `/api/`             | `{"status": "backend running"}`              |
| GET    | `/api/healthz`      | health probe                                 |
| GET    | `/api/ohlc`         | raw candles for one symbol/exchange/tf       |
| POST   | `/api/analyze-image`| inspect just an uploaded chart screenshot    |
| POST   | `/api/analyze`      | full multi-timeframe + image analysis        |

## Limitations

- TradingView data may not match Quotex exactly.
- OTC Quotex charts often do not match TradingView data at all.
- Screenshot analysis is visual confirmation only — not exact OHLC
  extraction. We do not calibrate the price axis.
- This system does not guarantee profit. Weak or conflicting evidence
  returns NO TRADE.

## Security & cleanliness

- TradingView credentials are read from environment variables only
  (`TV_USERNAME`, `TV_PASSWORD`); they are never stored in code.
- Uploaded images are processed in memory and never written to disk.
- Image type and size are validated (8 MB max; PNG/JPG/WebP only).
- CORS is enabled for development convenience.
