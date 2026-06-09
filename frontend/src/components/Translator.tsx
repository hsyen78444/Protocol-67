"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Ico } from "./Icons";
import { CountUp } from "./CountUp";
import { useApp } from "@/context/AppContext";
import { p67Translate, P67_EXAMPLES } from "@/lib/engine";
import type { TranslationResult } from "@/lib/types";

type Status = "empty" | "loading" | "result" | "error";

const PIPE_STEPS = [
  { label: "Tokenising input", Ic: Ico.scan },
  { label: "Matching slang lexicon", Ic: Ico.tag },
  { label: "Scoring sentiment", Ic: Ico.pulse },
  { label: "Estimating confidence", Ic: Ico.gauge },
];

function HighlightedOutput({
  text,
  unknown,
}: {
  text: string;
  unknown: string[];
}) {
  if (!unknown.length) return <span>{text}</span>;
  const pattern = new RegExp(
    "(" +
      unknown.map((u) => u.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") +
      ")",
    "ig",
  );
  const parts = text.split(pattern);
  return (
    <span>
      {parts.map((p, i) =>
        unknown.some((u) => u.toLowerCase() === p.toLowerCase()) ? (
          <mark key={i} title="Unrecognised term — sent to review queue">
            {p}
          </mark>
        ) : (
          <span key={i}>{p}</span>
        ),
      )}
    </span>
  );
}

function SentimentCard({ result }: { result: TranslationResult }) {
  const map = {
    positive: { cls: "s-pos", dot: "bg-pos", label: "Positive" },
    neutral: { cls: "s-neu", dot: "bg-neu", label: "Neutral" },
    negative: { cls: "s-neg", dot: "bg-neg", label: "Negative" },
  };
  const m = map[result.sentiment];
  const pct = ((result.sentiment_score + 1) / 2) * 100;
  const mid = 50;
  const left = Math.min(pct, mid);
  const width = Math.abs(pct - mid);
  return (
    <div className="a-card span-4 fade-up">
      <div className="a-head">
        <Ico.pulse style={{ width: 14, height: 14 }} /> Sentiment
      </div>
      <div className={"senti-badge " + m.cls}>
        <span className={"senti-dot " + m.dot} />
        {m.label}
      </div>
      <div>
        <div className="senti-bar">
          <div
            className={"senti-fill " + m.dot}
            style={{ left: left + "%", width: width + "%" }}
          />
        </div>
        <div className="senti-scale" style={{ marginTop: 6 }}>
          <span>negative</span>
          <span>neutral</span>
          <span>positive</span>
        </div>
      </div>
      <div className="conf-meta">
        polarity score · {result.sentiment_score > 0 ? "+" : ""}
        {result.sentiment_score.toFixed(2)}
      </div>
    </div>
  );
}

function ConfidenceCard({ result }: { result: TranslationResult }) {
  const [w, setW] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setW(result.confidence * 100), 60);
    return () => clearTimeout(t);
  }, [result]);
  const pctNum = Math.round(result.confidence * 100);
  const level =
    result.confidence >= 0.85
      ? "high"
      : result.confidence >= 0.7
        ? "moderate"
        : "low";
  return (
    <div className="a-card span-3 fade-up" style={{ animationDelay: ".05s" }}>
      <div className="a-head">
        <Ico.gauge style={{ width: 14, height: 14 }} /> Confidence
      </div>
      <div className="conf-num">
        <CountUp value={pctNum} />
        <small>%</small>
      </div>
      <div className="conf-track">
        <div className="conf-fill" style={{ width: w + "%" }} />
      </div>
      <div className="conf-meta">{level} certainty</div>
    </div>
  );
}

function DetectedCard({ result }: { result: TranslationResult }) {
  return (
    <div className="a-card span-5 fade-up" style={{ animationDelay: ".1s" }}>
      <div className="a-head">
        <Ico.tag style={{ width: 14, height: 14 }} /> Detected slang ·{" "}
        {result.detected_slang_terms.length}
      </div>
      {result.detected_slang_terms.length === 0 ? (
        <div className="empty-terms">
          No non-standard terms found — input reads as standard English.
        </div>
      ) : (
        <div className="terms-wrap">
          {result.detected_slang_terms.map((t, i) => (
            <span className="term" key={i}>
              <b>{t.term}</b>
              <span className="arrow">→</span>
              <span className="mean">{t.meaning}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function UnknownCard({ result }: { result: TranslationResult }) {
  const has = result.unknown_terms.length > 0;
  return (
    <div className="a-card span-7 fade-up" style={{ animationDelay: ".15s" }}>
      <div className="a-head">
        <Ico.alert style={{ width: 14, height: 14 }} /> Unknown terms ·{" "}
        {result.unknown_terms.length}
      </div>
      {has ? (
        <div className="terms-wrap">
          {result.unknown_terms.map((t, i) => (
            <span className="term unknown" key={i}>
              <span className="pip" />
              {t}
            </span>
          ))}
        </div>
      ) : (
        <div className="empty-terms">
          Full lexical coverage — every term was recognised by the model.
        </div>
      )}
      {has && (
        <div className="conf-meta">
          flagged for active learning · awaiting human review
        </div>
      )}
    </div>
  );
}

function MetaCard({ result }: { result: TranslationResult }) {
  return (
    <div className="a-card span-5 fade-up" style={{ animationDelay: ".2s" }}>
      <div className="a-head">
        <Ico.cpu style={{ width: 14, height: 14 }} /> Model trace
      </div>
      <div className="meta-grid">
        <div className="meta-item">
          <span className="meta-k">model</span>
          <span className="meta-v">{result.model_version}</span>
        </div>
        <div className="meta-item">
          <span className="meta-k">tokens</span>
          <span className="meta-v">{result.tokens}</span>
        </div>
        <div className="meta-item">
          <span className="meta-k">latency</span>
          <span className="meta-v">{result.latency_ms} ms</span>
        </div>
        <div className="meta-item">
          <span className="meta-k">coverage</span>
          <span className="meta-v">
            {result.detected_slang_terms.length}/
            {result.detected_slang_terms.length + result.unknown_terms.length ||
              "—"}
          </span>
        </div>
      </div>
    </div>
  );
}

function sameTranslationResult(
  a: TranslationResult | null,
  b: TranslationResult | null,
) {
  return JSON.stringify(a) === JSON.stringify(b);
}

export function Translator() {
  const router = useRouter();
  const {
    toast,
    ingestUnknowns,
    bumpTranslations,
    openFeedback,
    currentInput,
    setCurrentInput,
    currentTranslation,
    setCurrentTranslation,
  } = useApp();
  const [input, setInput] = useState(() => currentInput || P67_EXAMPLES[0]);
  const [result, setResult] = useState<TranslationResult | null>(
    () => currentTranslation || null,
  );
  const [status, setStatus] = useState<Status>(() =>
    currentTranslation ? "result" : "empty",
  );
  const [stepIdx, setStepIdx] = useState(0);
  const [copied, setCopied] = useState(false);
  const taRef = useRef<HTMLTextAreaElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (status !== "loading") {
      setStepIdx(0);
      return;
    }
    let i = 0;
    setStepIdx(0);
    const iv = setInterval(() => {
      i++;
      setStepIdx(Math.min(i, PIPE_STEPS.length - 1));
    }, 240);
    return () => clearInterval(iv);
  }, [status]);

  const runTranslate = useCallback(() => {
    if (!input.trim() || status === "loading") return;
    setStatus("loading");
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      try {
        const res = p67Translate(input);
        setResult(res);
        setStatus("result");
        bumpTranslations();
        const added = ingestUnknowns(res);
        if (added > 0)
          toast(
            `${added} unknown term${added > 1 ? "s" : ""} sent to review queue`,
            "info",
          );
      } catch {
        setStatus("error");
      }
    }, 1080);
  }, [input, status, bumpTranslations, ingestUnknowns, toast]);

  const onKey = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      runTranslate();
    }
  };

  const copy = () => {
    if (result) navigator.clipboard?.writeText(result.formal_translation);
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };

  const changeInput = (v: string) => {
    setInput(v);
    if (status === "error") setStatus("empty");
  };

  // persist input to app context
  useEffect(() => {
    if (input !== currentInput) setCurrentInput(input);
  }, [input, currentInput, setCurrentInput]);

  // persist translation result to app context
  useEffect(() => {
    if (result) {
      const same = sameTranslationResult(currentTranslation, result);
      if (!same) setCurrentTranslation(result);
    }
  }, [result, currentTranslation, setCurrentTranslation]);

  // If the provider loads saved state after this component mounted,
  // sync it into local state (but avoid overwriting live edits).
  useEffect(() => {
    if (currentInput && currentInput !== input) setInput(currentInput);
  }, [currentInput]);

  useEffect(() => {
    if (!currentTranslation) {
      if (result) {
        setResult(null);
        setStatus("empty");
      }
      return;
    }
    // sync once when provider restores a saved translation
    if (!sameTranslationResult(currentTranslation, result)) {
      setResult(currentTranslation);
      setStatus("result");
    }
  }, [currentTranslation]);

  const newUnknowns = result && result.unknown_terms.length > 0;

  return (
    <>
      <div style={{ marginTop: 26 }} className="eyebrow">
        Live translation console
      </div>
      <div className="console">
        {/* SOURCE */}
        <div className="pane source">
          <div className="pane-head">
            <div className="pane-title">
              <Ico.edit style={{ width: 14, height: 14 }} /> Source ·
              non-standard input
            </div>
            {input && (
              <button
                className="act-btn"
                style={{ padding: "5px 9px", fontSize: 12 }}
                onClick={() => {
                  changeInput("");
                  taRef.current?.focus();
                }}
              >
                Clear
              </button>
            )}
          </div>
          <textarea
            ref={taRef}
            className="input-area"
            value={input}
            onKeyDown={onKey}
            onChange={(e) => changeInput(e.target.value)}
            placeholder={
              "Paste slang, memes or chat language here…\ne.g. bro is cooked fr, this got me tweaking ngl"
            }
          />
          <div>
            <span className="chip-label">Try an example</span>
            <div className="chips-row">
              {P67_EXAMPLES.map((ex, i) => (
                <button
                  className="chip"
                  key={i}
                  title={ex}
                  onClick={() => changeInput(ex)}
                >
                  {ex.length > 38 ? ex.slice(0, 36) + "…" : ex}
                </button>
              ))}
            </div>
          </div>
          <div className="source-foot">
            <button
              className="btn-primary"
              onClick={runTranslate}
              disabled={!input.trim() || status === "loading"}
            >
              {status === "loading" ? (
                <>
                  <span className="spinner" /> Analysing…
                </>
              ) : (
                <>
                  <Ico.bolt style={{ width: 17, height: 17 }} /> Translate{" "}
                  <span className="kbd">⌘↵</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* OUTPUT */}
        <div className="pane output">
          <div className="pane-head">
            <div className="pane-title">
              <Ico.translate style={{ width: 14, height: 14 }} /> Formal English
            </div>
            {status === "result" && result && (
              <span className="conf-meta" style={{ fontSize: 11 }}>
                {result.tokens} tokens · {result.latency_ms}ms
              </span>
            )}
          </div>
          <div className="output-body">
            {status === "empty" && (
              <div className="placeholder">
                <Ico.brain />
                <p>
                  Your formal translation will appear here, with full linguistic
                  analysis below.
                </p>
              </div>
            )}
            {status === "loading" && (
              <div className="pipeline">
                {PIPE_STEPS.map((s, i) => {
                  const st =
                    i < stepIdx ? "done" : i === stepIdx ? "active" : "";
                  return (
                    <div className={"pipe-step " + st} key={i}>
                      <span className="pipe-ico">
                        {i < stepIdx ? (
                          <Ico.check style={{ width: 12, height: 12 }} />
                        ) : i === stepIdx ? (
                          <span className="spinner" />
                        ) : (
                          <s.Ic style={{ width: 12, height: 12 }} />
                        )}
                      </span>
                      {s.label}
                    </div>
                  );
                })}
              </div>
            )}
            {status === "error" && (
              <div className="err-state">
                <Ico.alert />
                <p style={{ margin: 0, fontWeight: 600 }}>
                  Translation service unavailable
                </p>
                <button className="btn-ghost" onClick={runTranslate}>
                  Retry request
                </button>
              </div>
            )}
            {status === "result" && result && (
              <>
                <div className="formal-text fade-up">
                  <HighlightedOutput
                    text={result.formal_translation}
                    unknown={result.unknown_terms}
                  />
                </div>
                <div className="output-actions">
                  <button className="act-btn" onClick={copy}>
                    {copied ? (
                      <>
                        <Ico.check style={{ width: 14, height: 14 }} /> Copied
                      </>
                    ) : (
                      <>
                        <Ico.copy style={{ width: 14, height: 14 }} /> Copy
                      </>
                    )}
                  </button>
                  <button
                    className="act-btn"
                    onClick={() => openFeedback(result)}
                  >
                    <Ico.flag style={{ width: 14, height: 14 }} /> Suggest a
                    correction
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* ANALYSIS */}
      {status === "result" && result && (
        <>
          <div style={{ marginTop: 26 }} className="eyebrow">
            Analysis
          </div>
          <div className="analysis">
            <SentimentCard result={result} />
            <ConfidenceCard result={result} />
            <DetectedCard result={result} />
            <UnknownCard result={result} />
            <MetaCard result={result} />
            {newUnknowns && (
              <div
                className="learn-banner fade-up"
                style={{ animationDelay: ".25s" }}
              >
                <span className="lb-ico">
                  <Ico.brain style={{ width: 18, height: 18 }} />
                </span>
                <p>
                  <b>
                    {result.unknown_terms.length} term
                    {result.unknown_terms.length > 1 ? "s" : ""}
                  </b>{" "}
                  the model hasn&apos;t learned yet{" "}
                  {result.unknown_terms.length > 1 ? "were" : "was"} added to
                  the active-learning queue.
                </p>
                <button
                  className="lb-go"
                  onClick={() => router.push("/review")}
                >
                  Review now <Ico.arrowR style={{ width: 15, height: 15 }} />
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </>
  );
}
