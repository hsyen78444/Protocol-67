"use client";

import { CountUp } from "./CountUp";
import { Ico } from "./Icons";
import type { Stats } from "@/lib/types";

export function StatsHeader({ stats }: { stats: Stats }) {
  const items = [
    { k: "Total translations", v: stats.translations, Ic: Ico.translate, tick: "var(--accent)" },
    { k: "Resolved unknown terms", v: stats.resolved, Ic: Ico.check, tick: "var(--pos)" },
    { k: "Feedback submitted", v: stats.feedback, Ic: Ico.msg, tick: "var(--neu)" },
  ];

  return (
    <div className="stats">
      {items.map((it) => (
        <div className="stat" key={it.k}>
          <div className="stat-label">
            <span className="stat-tick" style={{ background: it.tick }} />
            {it.k}
          </div>
          <div className="stat-num">
            <CountUp value={it.v} />
          </div>
        </div>
      ))}
    </div>
  );
}
