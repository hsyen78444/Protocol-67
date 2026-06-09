"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Ico } from "./Icons";
import { MODEL_VERSION } from "@/lib/engine";

export function TopBar({ queueCount }: { queueCount: number }) {
  const pathname = usePathname();

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <div className="brand">
          <div className="brand-mark">67</div>
          <div className="brand-text">
            <div className="brand-name">Protocol&nbsp;67</div>
            <div className="brand-sub">Brainrot → English</div>
          </div>
        </div>

        <nav className="nav">
          <Link
            href="/"
            className={"nav-btn" + (pathname === "/" ? " active" : "")}
          >
            <Ico.translate style={{ width: 17, height: 17 }} />
            <span className="lbl">Translator</span>
          </Link>
          <Link
            href="/review"
            className={"nav-btn" + (pathname === "/review" ? " active" : "")}
          >
            <Ico.queue style={{ width: 17, height: 17 }} />
            <span className="lbl">Review queue</span>
            {queueCount > 0 && <span className="nav-badge">{queueCount}</span>}
          </Link>
        </nav>

        <div className="ver-pill">
          <span className="pulse-dot" />
          {MODEL_VERSION}
        </div>
      </div>
    </header>
  );
}
