"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  fetchStats,
  fetchUnknownTerms,
  ignoreUnknownTerm,
  resolveUnknownTerm,
  submitTranslationFeedback,
} from "@/lib/api";
import type {
  QueueRow,
  Stats,
  Toast,
  ToastKind,
  TranslationResult,
} from "@/lib/types";

interface AppState {
  stats: Stats;
  queue: QueueRow[];
  toasts: Toast[];
  feedbackFor: TranslationResult | null;
  currentInput: string;
  currentTranslation: TranslationResult | null;
  hydrated: boolean;
  pendingCount: number;
  toast: (msg: string, kind?: ToastKind) => void;
  ingestUnknowns: (res: TranslationResult) => number;
  setCurrentInput: (v: string) => void;
  setCurrentTranslation: (r: TranslationResult | null) => void;
  bumpTranslations: () => void;
  submitFeedback: (data: { corrected: string; notes: string }) => void;
  openFeedback: (res: TranslationResult) => void;
  closeFeedback: () => void;
  resolveTerm: (id: string) => void;
  ignoreTerm: (id: string) => void;
  editProposed: (id: string, val: string) => void;
}

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [stats, setStats] = useState<Stats>({
    translations: 0,
    resolved: 0,
    feedback: 0,
  });
  const [queue, setQueue] = useState<QueueRow[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [feedbackFor, setFeedbackFor] = useState<TranslationResult | null>(
    null,
  );
  const [currentInput, setCurrentInput] = useState("");
  const [currentTranslation, setCurrentTranslation] =
    useState<TranslationResult | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const toastId = useRef(0);
  const savedInputRef = useRef<string | null>(null);
  const savedTranslationRef = useRef<string | null>(null);

  useEffect(() => {
    try {
      const savedIn = localStorage.getItem("p67_currentInput");
      const savedRes = localStorage.getItem("p67_currentTranslation");

      if (savedIn) {
        savedInputRef.current = savedIn;
        setCurrentInput(savedIn);
      }

      if (savedRes) {
        try {
          savedTranslationRef.current = savedRes;
          setCurrentTranslation(JSON.parse(savedRes));
        } catch {
          localStorage.removeItem("p67_currentTranslation");
        }
      }
    } catch {
      // Local storage is optional for the app to function.
    }

    setHydrated(true);
  }, []);

  useEffect(() => {
    try {
      if (savedInputRef.current === currentInput) return;
      localStorage.setItem("p67_currentInput", currentInput);
      savedInputRef.current = currentInput;
    } catch {}
  }, [currentInput]);

  useEffect(() => {
    try {
      const serialized = currentTranslation
        ? JSON.stringify(currentTranslation)
        : null;
      if (savedTranslationRef.current === serialized) return;

      if (serialized) {
        localStorage.setItem("p67_currentTranslation", serialized);
      } else {
        localStorage.removeItem("p67_currentTranslation");
      }

      savedTranslationRef.current = serialized;
    } catch {}
  }, [currentTranslation]);

  const toast = useCallback((msg: string, kind: ToastKind = "ok") => {
    const id = ++toastId.current;
    setToasts((t) => [...t, { id, msg, kind }]);
    setTimeout(
      () =>
        setToasts((t) => t.map((x) => (x.id === id ? { ...x, out: true } : x))),
      2600,
    );
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 2950);
  }, []);

  const refreshBackendState = useCallback(async () => {
    try {
      const [nextStats, nextQueue] = await Promise.all([
        fetchStats(),
        fetchUnknownTerms(),
      ]);
      setStats(nextStats);
      setQueue(nextQueue);
    } catch {
      toast("Backend unavailable - start FastAPI on port 8000", "info");
    }
  }, [toast]);

  useEffect(() => {
    if (hydrated) void refreshBackendState();
  }, [hydrated, refreshBackendState]);

  const ingestUnknowns = useCallback(
    (res: TranslationResult): number => {
      if (!res.unknown_terms.length) return 0;
      void refreshBackendState();
      return res.unknown_terms.length;
    },
    [refreshBackendState],
  );

  const bumpTranslations = useCallback(() => {
    setStats((s) => ({ ...s, translations: s.translations + 1 }));
    void refreshBackendState();
  }, [refreshBackendState]);

  const submitFeedback = useCallback(
    async (data: { corrected: string; notes: string }) => {
      if (!feedbackFor) return;

      try {
        await submitTranslationFeedback({
          result: feedbackFor,
          corrected: data.corrected,
          notes: data.notes,
        });
        setFeedbackFor(null);
        await refreshBackendState();
        toast("Feedback logged - thanks for improving the model");
      } catch {
        toast("Could not submit feedback to the backend", "info");
      }
    },
    [feedbackFor, refreshBackendState, toast],
  );

  const openFeedback = useCallback(
    (res: TranslationResult) => setFeedbackFor(res),
    [],
  );
  const closeFeedback = useCallback(() => setFeedbackFor(null), []);

  const resolveTerm = useCallback(
    async (id: string) => {
      const row = queue.find((item) => item.id === id);
      if (!row?.proposed.trim()) {
        toast("Add a proposed meaning before resolving", "info");
        return;
      }

      try {
        await resolveUnknownTerm(id, row.proposed.trim());
        await refreshBackendState();
        toast("Term added to lexicon - model will retrain");
      } catch {
        toast("Could not resolve term in the backend", "info");
      }
    },
    [queue, refreshBackendState, toast],
  );

  const ignoreTerm = useCallback(
    async (id: string) => {
      try {
        await ignoreUnknownTerm(id);
        await refreshBackendState();
        toast("Term ignored", "info");
      } catch {
        toast("Could not ignore term in the backend", "info");
      }
    },
    [refreshBackendState, toast],
  );

  const editProposed = useCallback((id: string, val: string) => {
    setQueue((q) => q.map((r) => (r.id === id ? { ...r, proposed: val } : r)));
  }, []);

  const pendingCount = queue.filter((q) => q.status === "pending").length;

  return (
    <AppContext.Provider
      value={{
        stats,
        queue,
        toasts,
        feedbackFor,
        pendingCount,
        hydrated,
        currentInput,
        currentTranslation,
        setCurrentInput,
        setCurrentTranslation,
        toast,
        ingestUnknowns,
        bumpTranslations,
        submitFeedback,
        openFeedback,
        closeFeedback,
        resolveTerm,
        ignoreTerm,
        editProposed,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
