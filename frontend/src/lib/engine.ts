/**
 * Mock translation engine that mirrors the FastAPI response contract.
 * Replace p67Translate() with a fetch() call to NEXT_PUBLIC_API_URL/translate
 * when the backend is ready.
 */

import type { TranslationResult, QueueRow } from "./types";

const MODEL_VERSION = "protocol-67 · v0.6.7";

interface PhraseEntry { f: string; s: number; }
interface WordEntry  { f: string; s: number; }
interface EmergingEntry { proposed: string; example: string; }

const P67_PHRASES: Record<string, PhraseEntry> = {
  "got me tweaking": { f: "is making me extremely anxious", s: -0.7 },
  "no cap": { f: "honestly", s: 0.1 },
  "fr fr": { f: "absolutely", s: 0.1 },
  "on god": { f: "I swear", s: 0.1 },
  "built different": { f: "exceptionally capable", s: 0.7 },
  "different breed": { f: "in a class of their own", s: 0.6 },
  "hits different": { f: "is distinctly better", s: 0.6 },
  "rent free": { f: "constantly on my mind", s: -0.1 },
  "main character": { f: "the centre of attention", s: 0.4 },
  "glow up": { f: "a remarkable improvement", s: 0.7 },
  "lock in": { f: "fully concentrate", s: 0.3 },
  "ate that": { f: "performed exceptionally", s: 0.8 },
  "sigma grindset": { f: "a self-reliant work ethic", s: 0.4 },
  "touch grass": { f: "reconnect with reality", s: -0.1 },
};

const P67_WORDS: Record<string, WordEntry> = {
  bro: { f: "my friend", s: 0 },
  bruh: { f: "my goodness", s: -0.2 },
  cooked: { f: "in serious trouble", s: -0.8 },
  fr: { f: "honestly", s: 0.05 },
  ngl: { f: "to be honest", s: 0 },
  tweaking: { f: "extremely anxious", s: -0.7 },
  bussin: { f: "excellent", s: 0.8 },
  mid: { f: "mediocre", s: -0.5 },
  cap: { f: "a lie", s: -0.3 },
  based: { f: "admirably authentic", s: 0.6 },
  cringe: { f: "embarrassing", s: -0.6 },
  lowkey: { f: "somewhat", s: 0 },
  highkey: { f: "very much", s: 0.1 },
  bet: { f: "understood", s: 0.2 },
  fam: { f: "close friends", s: 0.3 },
  deadass: { f: "seriously", s: 0 },
  slay: { f: "performing impressively", s: 0.7 },
  ate: { f: "excelled", s: 0.7 },
  rizz: { f: "charisma", s: 0.5 },
  sus: { f: "suspicious", s: -0.4 },
  sigma: { f: "self-assured", s: 0.3 },
  goated: { f: "the greatest of all time", s: 0.9 },
  fire: { f: "excellent", s: 0.8 },
  slaps: { f: "is excellent", s: 0.7 },
  salty: { f: "bitter", s: -0.5 },
  simp: { f: "overly devoted admirer", s: -0.2 },
  stan: { f: "a devoted fan", s: 0.3 },
  vibe: { f: "atmosphere", s: 0.3 },
  vibes: { f: "atmosphere", s: 0.3 },
  sheesh: { f: "wow", s: 0.4 },
  finna: { f: "going to", s: 0 },
  tryna: { f: "trying to", s: 0 },
  istg: { f: "I swear", s: 0 },
  smh: { f: "which is disappointing", s: -0.4 },
  tbh: { f: "to be honest", s: 0 },
  ong: { f: "I swear", s: 0.05 },
  opp: { f: "an adversary", s: -0.4 },
  drip: { f: "stylish attire", s: 0.5 },
  ratio: { f: "decisively outdone", s: -0.3 },
  yeet: { f: "throw forcefully", s: 0.1 },
  goofy: { f: "foolish", s: -0.3 },
  pressed: { f: "agitated", s: -0.4 },
  bopping: { f: "thoroughly enjoyable", s: 0.6 },
  banger: { f: "an outstanding piece of work", s: 0.8 },
  clutch: { f: "decisive and timely", s: 0.6 },
  cooking: { f: "doing exceptionally well", s: 0.6 },
};

export const P67_EMERGING: Record<string, EmergingEntry> = {
  "skibidi": { proposed: "chaotic or nonsensical (meme-derived)", example: "this skibidi energy is wild" },
  "fanum tax": { proposed: "an informal toll where a friend takes some of your food", example: "the fanum tax got me feeling some way" },
  "delulu": { proposed: "delusional, holding unrealistic beliefs", example: "you're being kinda delulu about this" },
  "gyatt": { proposed: "an exclamation of surprise or admiration", example: "gyatt, did you see that score" },
  "mewing": { proposed: "a jaw-positioning self-improvement trend", example: "he was mewing through the whole lecture" },
  "looksmaxxing": { proposed: "maximising one's physical appearance", example: "the whole group chat is looksmaxxing now" },
  "huzz": { proposed: "an ambiguous group referent (context-dependent)", example: "the huzz pulled up to the library" },
  "glazing": { proposed: "excessively praising someone", example: "stop glazing the lecturer fr" },
};

export const P67_EXAMPLES = [
  "bro is cooked fr, this assignment got me tweaking ngl",
  "no cap that fit is bussin, you ate fr fr",
  "lowkey this lecture mid but the prof kinda based ngl",
  "the fanum tax got me feeling delulu, this skibidi energy is wild",
  "deadass the new update slaps, devs cooking fr",
];

function p67Hash(str: string): number {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h);
}

function clamp(v: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, v));
}

function titleCaseSentences(text: string): string {
  let out = text.replace(/\s+/g, " ").trim();
  out = out.replace(/\s+([,.!?;:])/g, "$1");
  out = out.replace(/([,;:])(?=\S)/g, "$1 ");
  out = out.replace(/(^\s*|[.!?]\s+)([a-z])/g, (_m, pre: string, ch: string) => pre + ch.toUpperCase());
  out = out.replace(/\bi\b/g, "I");
  if (out && !/[.!?]$/.test(out)) out += ".";
  return out;
}

export function p67Translate(raw: string): TranslationResult {
  const input = (raw || "").trim();
  const lower = input.toLowerCase();
  const detected: TranslationResult["detected_slang_terms"] = [];
  const detectedKeys = new Set<string>();
  const unknown: string[] = [];

  Object.keys(P67_EMERGING).forEach((term) => {
    const re = new RegExp("\\b" + term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "i");
    if (re.test(lower)) unknown.push(term);
  });

  let working = " " + input + " ";

  const phraseKeys = Object.keys(P67_PHRASES).sort((a, b) => b.length - a.length);
  phraseKeys.forEach((ph) => {
    const re = new RegExp("\\b" + ph.replace(/\s+/g, "\\s+") + "\\b", "ig");
    if (re.test(working)) {
      detected.push({ term: ph, meaning: P67_PHRASES[ph].f, s: P67_PHRASES[ph].s });
      detectedKeys.add(ph);
      working = working.replace(re, " " + P67_PHRASES[ph].f + " ");
    }
  });

  Object.keys(P67_WORDS).forEach((w) => {
    const re = new RegExp("\\b" + w + "\\b", "ig");
    if (re.test(working)) {
      detected.push({ term: w, meaning: P67_WORDS[w].f, s: P67_WORDS[w].s });
      detectedKeys.add(w);
      working = working.replace(re, " " + P67_WORDS[w].f + " ");
    }
  });

  const formal_translation = titleCaseSentences(working) || "—";

  let score = 0;
  detected.forEach((d) => { score += d.s; });
  if (detected.length) score = score / Math.sqrt(detected.length);
  score = clamp(score, -1, 1);

  let sentiment: TranslationResult["sentiment"] = "neutral";
  if (score > 0.22) sentiment = "positive";
  else if (score < -0.22) sentiment = "negative";

  const signals = detected.length + unknown.length;
  const coverage = signals === 0 ? 0.85 : detected.length / signals;
  const hash = p67Hash(lower || "x");
  const jitter = ((hash % 9) - 4) / 100;
  let confidence = 0.72 + coverage * 0.24 + jitter;
  if (detected.length === 0 && unknown.length === 0) confidence = 0.9 + jitter;
  confidence = clamp(confidence, 0.55, 0.985);

  const tokens = input ? input.split(/\s+/).filter(Boolean).length : 0;
  const latency_ms = 380 + (hash % 520);

  return {
    input,
    formal_translation,
    sentiment,
    sentiment_score: Math.round(score * 100) / 100,
    confidence: Math.round(confidence * 1000) / 1000,
    detected_slang_terms: detected,
    unknown_terms: unknown,
    model_version: MODEL_VERSION,
    tokens,
    latency_ms,
  };
}

export function p67SeedQueue(): QueueRow[] {
  const seeds = ["skibidi", "fanum tax", "delulu", "gyatt", "mewing"];
  return seeds.map((term, i) => ({
    id: "seed-" + i,
    term,
    example: P67_EMERGING[term].example,
    proposed: P67_EMERGING[term].proposed,
    status: "pending" as const,
    occurrences: 2 + ((p67Hash(term) % 14)),
    first_seen: ["2d ago", "5h ago", "1d ago", "3d ago", "6h ago"][i] || "recently",
  }));
}

export { MODEL_VERSION };
