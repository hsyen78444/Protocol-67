export interface DetectedTerm {
  term: string;
  meaning: string;
  s: number;
}

export interface TranslationResult {
  input: string;
  formal_translation: string;
  sentiment: "positive" | "neutral" | "negative";
  sentiment_score: number;
  confidence: number;
  detected_slang_terms: DetectedTerm[];
  unknown_terms: string[];
  model_version: string;
  tokens: number;
  latency_ms: number;
  translation_id?: number;
}

export interface QueueRow {
  id: string;
  term: string;
  example: string;
  proposed: string;
  status: "pending" | "resolved" | "ignored";
  occurrences: number;
  first_seen: string;
  isNew?: boolean;
}

export interface Stats {
  translations: number;
  resolved: number;
  feedback: number;
}

export type ToastKind = "ok" | "info";

export interface Toast {
  id: number;
  msg: string;
  kind: ToastKind;
  out?: boolean;
}
