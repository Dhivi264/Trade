export type Decision = "BUY" | "SELL" | "NO TRADE";

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface SupportResistance {
  type: "support" | "resistance";
  price: number;
}

export interface Evidence {
  one_hour_trend?: string;
  fifteen_min_structure?: string;
  five_min_move?: string;
  image_bias?: string;
  image_quality?: string;
  support_resistance?: SupportResistance[];
}

export interface AnalyzeResponse {
  decision: Decision;
  confidence: number;
  reason: string;
  evidence?: Evidence;
  warnings?: string[];
  data_source?: string;
  candles_preview?: Candle[];
}

export interface DetectResponse {
  symbol: string | null;
  exchange: string | null;
  is_otc: boolean;
  raw_text: string;
  confidence: number;
  candidates: string[];
  reason: string;
}
