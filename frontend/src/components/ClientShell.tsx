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
    </>
  );
}
