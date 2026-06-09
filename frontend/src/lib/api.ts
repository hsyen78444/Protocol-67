import type { QueueRow, Stats, TranslationResult } from "./types";

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000")
  .replace(/\/+$/, "");

type BackendSentiment = "positive" | "neutral" | "negative";

interface BackendTranslateResponse {
  input: string;
  formal_translation: string;
  sentiment: BackendSentiment;
  confidence: number;
  detected_slang_terms: Array<string | { term: string; meaning?: string; s?: number }>;
  unknown_terms: string[];
  model_version: string;
  translation_id?: number;
}

interface BackendStats {
  total_translations: number;
  total_feedback_items: number;
  resolved_unknown_terms: number;
}

interface BackendUnknownTerm {
  id: number;
  term: string;
  frequency: number;
  status: "open" | "reviewing" | "resolved" | "ignored";
  example_text: string;
  proposed_meaning: string | null;
}

interface BackendUnknownTermsResponse {
  items: BackendUnknownTerm[];
}

async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // Keep the HTTP status text when the server did not return JSON.
    }
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function sentimentScore(sentiment: BackendSentiment): number {
  if (sentiment === "positive") return 0.65;
  if (sentiment === "negative") return -0.65;
  return 0;
}

function tokenCount(text: string): number {
  return text.trim() ? text.trim().split(/\s+/).length : 0;
}

function normalizeTranslation(
  payload: BackendTranslateResponse,
  latencyMs: number,
): TranslationResult {
  const score = sentimentScore(payload.sentiment);

  return {
    input: payload.input,
    formal_translation: payload.formal_translation,
    sentiment: payload.sentiment,
    sentiment_score: score,
    confidence: payload.confidence,
    detected_slang_terms: payload.detected_slang_terms.map((term) => {
      if (typeof term === "string") {
        return {
          term,
          meaning: "Detected by backend lexicon",
          s: score,
        };
      }
      return {
        term: term.term,
        meaning: term.meaning || "Detected by backend lexicon",
        s: term.s ?? score,
      };
    }),
    unknown_terms: payload.unknown_terms,
    model_version: payload.model_version,
    tokens: tokenCount(payload.input),
    latency_ms: latencyMs,
    translation_id: payload.translation_id,
  };
}

function toStats(payload: BackendStats): Stats {
  return {
    translations: payload.total_translations,
    resolved: payload.resolved_unknown_terms,
    feedback: payload.total_feedback_items,
  };
}

function toQueueRow(item: BackendUnknownTerm): QueueRow {
  return {
    id: String(item.id),
    term: item.term,
    example: item.example_text || "",
    proposed: item.proposed_meaning || "",
    status: item.status === "resolved"
      ? "resolved"
      : item.status === "ignored"
        ? "ignored"
        : "pending",
    occurrences: item.frequency,
    first_seen: "from backend",
  };
}

export async function translateText(text: string): Promise<TranslationResult> {
  const started = performance.now();
  const payload = await requestJson<BackendTranslateResponse>("/translate", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
  return normalizeTranslation(payload, Math.round(performance.now() - started));
}

export async function fetchStats(): Promise<Stats> {
  return toStats(await requestJson<BackendStats>("/stats"));
}

export async function fetchUnknownTerms(): Promise<QueueRow[]> {
  const statuses = ["open", "reviewing", "resolved", "ignored"] as const;
  const pages = await Promise.all(
    statuses.map((status) =>
      requestJson<BackendUnknownTermsResponse>(
        `/unknown-terms?status=${status}&page=0&limit=100`,
      ),
    ),
  );
  return pages.flatMap((page) => page.items.map(toQueueRow));
}

export async function submitTranslationFeedback(args: {
  result: TranslationResult;
  corrected: string;
  notes: string;
}): Promise<void> {
  await requestJson("/feedback", {
    method: "POST",
    body: JSON.stringify({
      translation_id: args.result.translation_id ?? null,
      input_text: args.result.input,
      original_translation: args.result.formal_translation,
      corrected_translation: args.corrected,
      notes: args.notes || null,
    }),
  });
}

export async function resolveUnknownTerm(id: string, proposed: string): Promise<void> {
  await requestJson(`/unknown-terms/${id}/resolve`, {
    method: "POST",
    body: JSON.stringify({ proposed_meaning: proposed }),
  });
}

export async function ignoreUnknownTerm(id: string): Promise<void> {
  await requestJson(`/unknown-terms/${id}/ignore`, { method: "POST" });
}
