"use client";

import { useApp } from "@/context/AppContext";
import { TopBar } from "./TopBar";
import { StatsHeader } from "./StatsHeader";
import { ToastHost } from "./ToastHost";
import { FeedbackModal } from "./FeedbackModal";

export function ClientShell({ children }: { children: React.ReactNode }) {
  const {
    pendingCount,
    stats,
    toasts,
    feedbackFor,
    submitFeedback,
    closeFeedback,
    hydrated,
    currentInput,
    currentTranslation,
  } = useApp();

  if (!hydrated) return null;

  return (
    <>
      <div className="bg-decoration" />
      <TopBar queueCount={pendingCount} />
      <div className="shell">
        <StatsHeader stats={stats} />
        {children}
      </div>
      {feedbackFor && (
        <FeedbackModal
          result={feedbackFor}
          onClose={closeFeedback}
          onSubmit={submitFeedback}
        />
      )}
      <ToastHost toasts={toasts} />
      <div
        style={{
          position: "fixed",
          right: 12,
          bottom: 12,
          background: "rgba(0,0,0,0.6)",
          color: "#fff",
          padding: "8px 10px",
          borderRadius: 8,
          fontSize: 12,
          zIndex: 60,
        }}
      >
        <div style={{ fontWeight: 700, marginBottom: 6 }}>DEBUG</div>
        <div
          style={{
            maxWidth: 300,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {currentInput || <i>empty</i>}
        </div>
        <div
          style={{ marginTop: 6, color: currentTranslation ? "#8f8" : "#f88" }}
        >
          {currentTranslation ? "translation present" : "no translation"}
        </div>
      </div>
    </>
  );
}
