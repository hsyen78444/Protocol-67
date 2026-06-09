"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Ico } from "./Icons";
import { useApp } from "@/context/AppContext";
import type { QueueRow } from "@/lib/types";

function highlightTerm(example: string, term: string) {
  const re = new RegExp("(" + term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
  const parts = example.split(re);
  return parts.map((p, i) =>
    p.toLowerCase() === term.toLowerCase()
      ? <span className="hl" key={i}>{p}</span>
      : <span key={i}>{p}</span>
  );
}

function QueueRowCard({
  row,
  onResolve,
  onIgnore,
  onEdit,
}: {
  row: QueueRow;
  onResolve: (id: string) => void;
  onIgnore: (id: string) => void;
  onEdit: (id: string, val: string) => void;
}) {
  const [leaving, setLeaving] = useState(false);

  const act = (fn: () => void) => {
    setLeaving(true);
    setTimeout(fn, 260);
  };

  return (
    <div className={"q-row" + (leaving ? " resolving" : "")}>
      <div className="q-main">
        <div className="q-term-line">
          <span className="q-term">{row.term}</span>
          {row.isNew && <span className="q-tag new">new</span>}
          <span className="q-tag occ">{row.occurrences}× seen</span>
          <span
            className="q-tag occ"
            style={{ background: "transparent", borderColor: "transparent", color: "var(--ink-ghost)" }}
          >
            first seen {row.first_seen}
          </span>
        </div>
        <p className="q-example">&quot;{highlightTerm(row.example, row.term)}&quot;</p>
        <div className="q-proposed">
          <span className="pk">proposed</span>
          <input
            value={row.proposed}
            onChange={(e) => onEdit(row.id, e.target.value)}
            aria-label="Proposed meaning"
          />
        </div>
      </div>
      <div className="q-actions">
        <button className="q-btn q-ignore" onClick={() => act(() => onIgnore(row.id))}>
          <Ico.x style={{ width: 14, height: 14 }} /> Ignore
        </button>
        <button className="q-btn q-resolve" onClick={() => act(() => onResolve(row.id))}>
          <Ico.check style={{ width: 15, height: 15 }} /> Add to lexicon
        </button>
      </div>
    </div>
  );
}

export function ReviewQueue() {
  const router = useRouter();
  const { queue, resolveTerm, ignoreTerm, editProposed } = useApp();
  const [filter, setFilter] = useState<"pending" | "resolved" | "ignored">("pending");

  const pending  = queue.filter((q) => q.status === "pending");
  const resolved = queue.filter((q) => q.status === "resolved");
  const ignored  = queue.filter((q) => q.status === "ignored");

  const shown = filter === "pending" ? pending : filter === "resolved" ? resolved : ignored;

  return (
    <>
      <div className="page-head">
        <div className="eyebrow">Active learning</div>
        <h1 className="page-title">Unknown-term review queue</h1>
        <p className="page-desc">
          Terms the model flagged as out-of-vocabulary, ranked for human review. Confirm a meaning to
          add it to the lexicon, or ignore noise. Every resolution sharpens the next model version.
        </p>
      </div>

      <div className="queue-toolbar">
        <div className="filter-tabs">
          {([["pending", "Pending", pending.length], ["resolved", "Resolved", resolved.length], ["ignored", "Ignored", ignored.length]] as const).map(
            ([k, label, n]) => (
              <button
                key={k}
                className={"filter-tab" + (filter === k ? " active" : "")}
                onClick={() => setFilter(k)}
              >
                {label} · {n}
              </button>
            )
          )}
        </div>
        <span className="queue-count">
          {pending.length} term{pending.length !== 1 ? "s" : ""} awaiting review
        </span>
      </div>

      <div className="queue">
        {shown.length === 0 ? (
          <div className="q-empty">
            <Ico.check style={{ color: "var(--pos)" }} />
            <p>
              {filter === "pending"
                ? "Queue is clear — the model is fully caught up."
                : "Nothing here yet."}
            </p>
            {filter === "pending" && (
              <button className="btn-ghost" style={{ marginTop: 16 }} onClick={() => router.push("/")}>
                Back to translator
              </button>
            )}
          </div>
        ) : (
          shown.map((row) => (
            <QueueRowCard
              key={row.id}
              row={row}
              onResolve={resolveTerm}
              onIgnore={ignoreTerm}
              onEdit={editProposed}
            />
          ))
        )}
      </div>
    </>
  );
}
