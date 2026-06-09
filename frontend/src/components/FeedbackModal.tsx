"use client";

import { useState, useEffect, useRef } from "react";
import { Ico } from "./Icons";
import type { TranslationResult } from "@/lib/types";

interface Props {
  result: TranslationResult;
  onClose: () => void;
  onSubmit: (data: { corrected: string; notes: string }) => void;
}

export function FeedbackModal({ result, onClose, onSubmit }: Props) {
  const [corrected, setCorrected] = useState(result.formal_translation);
  const [notes, setNotes] = useState("");
  const [touched, setTouched] = useState(false);
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    ref.current?.focus();
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [onClose]);

  const invalid = !corrected.trim();

  const submit = () => {
    setTouched(true);
    if (invalid) return;
    onSubmit({ corrected: corrected.trim(), notes: notes.trim() });
  };

  return (
    <div
      className="overlay"
      onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="modal" role="dialog" aria-modal="true">
        <div className="modal-head">
          <div>
            <h3 className="modal-title">Improve this translation</h3>
            <p className="modal-sub">
              Your correction is logged against <b>{result.model_version}</b> and feeds the next training round.
            </p>
          </div>
          <button className="modal-x" onClick={onClose} aria-label="Close">
            <Ico.x style={{ width: 16, height: 16 }} />
          </button>
        </div>

        <div className="modal-body">
          <div className="field">
            <label>Original input</label>
            <div className="orig">{result.input}</div>
          </div>

          <div className="field">
            <label>Corrected formal translation</label>
            <textarea
              ref={ref}
              rows={3}
              value={corrected}
              onChange={(e) => setCorrected(e.target.value)}
              onBlur={() => setTouched(true)}
              style={touched && invalid ? { borderColor: "var(--neg)" } : undefined}
            />
            {touched && invalid ? (
              <span className="err">
                <Ico.alert style={{ width: 13, height: 13 }} /> A corrected translation is required.
              </span>
            ) : (
              <span className="hint">Edit the model&apos;s output to what it should have said.</span>
            )}
          </div>

          <div className="field">
            <label>
              Notes{" "}
              <span style={{ textTransform: "none", letterSpacing: 0, color: "var(--ink-ghost)" }}>
                (optional)
              </span>
            </label>
            <textarea
              rows={2}
              value={notes}
              placeholder="e.g. 'cooked' here means exhausted, not in trouble"
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
        </div>

        <div className="modal-foot">
          <button className="btn-ghost" onClick={onClose}>Cancel</button>
          <button
            className="btn-primary"
            style={{ flex: "none", padding: "11px 20px" }}
            onClick={submit}
          >
            <Ico.check style={{ width: 16, height: 16 }} /> Submit feedback
          </button>
        </div>
      </div>
    </div>
  );
}
