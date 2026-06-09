"use client";

import { Ico } from "./Icons";
import type { Toast } from "@/lib/types";

export function ToastHost({ toasts }: { toasts: Toast[] }) {
  return (
    <div className="toast-wrap">
      {toasts.map((t) => (
        <div className={"toast" + (t.out ? " out" : "")} key={t.id}>
          <span className={"t-ico " + (t.kind || "ok")}>
            {t.kind === "info"
              ? <Ico.spark style={{ width: 13, height: 13, color: "#fff" }} />
              : <Ico.check style={{ width: 13, height: 13, color: "#fff" }} />}
          </span>
          {t.msg}
        </div>
      ))}
    </div>
  );
}
