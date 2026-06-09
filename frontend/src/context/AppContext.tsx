"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  useEffect,
  type ReactNode,
} from "react";
import { p67SeedQueue, P67_EMERGING } from "@/lib/engine";
import type {
  Stats,
  QueueRow,
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
    translations: 128,
    resolved: 41,
    feedback: 17,
  });
  const [queue, setQueue] = useState<QueueRow[]>(() => p67SeedQueue());
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [feedbackFor, setFeedbackFor] = useState<TranslationResult | null>(
    null,
  );
  const [currentInput, setCurrentInput] = useState<string>("");
  const [currentTranslation, setCurrentTranslation] =
    useState<TranslationResult | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const toastId = useRef(0);
  const savedInputRef = useRef<string | null>(null);
  const savedTranslationRef = useRef<string | null>(null);

  // Persist translator state to localStorage so it survives navigation/reloads
  useEffect(() => {
    try {
      const savedIn = localStorage.getItem("p67_currentInput");
      const savedRes = localStorage.getItem("p67_currentTranslation");
      if (savedIn) {
        savedInputRef.current = savedIn;
        setCurrentInput(savedIn);
        console.debug(
          "AppProvider: loaded currentInput from localStorage",
          savedIn,
        );
      }
      if (savedRes) {
        try {
          const parsed = JSON.parse(savedRes);
          savedTranslationRef.current = savedRes;
          setCurrentTranslation(parsed);
          console.debug(
            "AppProvider: loaded currentTranslation from localStorage",
            parsed,
          );
        } catch (e) {
          console.debug(
            "AppProvider: failed to parse saved currentTranslation",
            e,
          );
        }
      }
    } catch (e) {
      // ignore
    }
    setHydrated(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    try {
      if (savedInputRef.current === currentInput) return;
      localStorage.setItem("p67_currentInput", currentInput);
      savedInputRef.current = currentInput;
      console.debug("AppProvider: saved currentInput", currentInput);
    } catch (e) {}
  }, [currentInput]);

  useEffect(() => {
    try {
      const serialized = currentTranslation
        ? JSON.stringify(currentTranslation)
        : null;
      if (savedTranslationRef.current === serialized) return;
      if (serialized)
        localStorage.setItem("p67_currentTranslation", serialized);
      else localStorage.removeItem("p67_currentTranslation");
      savedTranslationRef.current = serialized;
      console.debug(
        "AppProvider: saved currentTranslation",
        currentTranslation,
      );
    } catch (e) {}
  }, [currentTranslation]);

  useEffect(() => {
    console.debug("AppProvider: current state change", {
      currentInput,
      currentTranslation,
    });
  }, [currentInput, currentTranslation]);

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

  const ingestUnknowns = useCallback((res: TranslationResult): number => {
    if (!res.unknown_terms.length) return 0;
    let added = 0;
    setQueue((q) => {
      const known = new Set(q.map((r) => r.term.toLowerCase()));
      const fresh: QueueRow[] = [];
      res.unknown_terms.forEach((term) => {
        if (!known.has(term.toLowerCase())) {
          const meta = P67_EMERGING[term] || {
            proposed: "",
            example: res.input,
          };
          fresh.push({
            id: "u-" + term + "-" + Date.now(),
            term,
            example: res.input,
            proposed: meta.proposed || "(needs a proposed meaning)",
            status: "pending",
            occurrences: 1,
            first_seen: "just now",
            isNew: true,
          });
          added++;
        }
      });
      const bumped = q.map((r) =>
        res.unknown_terms.some(
          (t) => t.toLowerCase() === r.term.toLowerCase(),
        ) && r.status === "pending"
          ? { ...r, occurrences: r.occurrences + 1 }
          : r,
      );
      return [...fresh, ...bumped];
    });
    return added;
  }, []);

  const bumpTranslations = useCallback(() => {
    setStats((s) => ({ ...s, translations: s.translations + 1 }));
  }, []);

  const submitFeedback = useCallback(
    (_data: { corrected: string; notes: string }) => {
      setStats((s) => ({ ...s, feedback: s.feedback + 1 }));
      setFeedbackFor(null);
      toast("Feedback logged — thanks for improving the model");
    },
    [toast],
  );

  const openFeedback = useCallback(
    (res: TranslationResult) => setFeedbackFor(res),
    [],
  );
  const closeFeedback = useCallback(() => setFeedbackFor(null), []);

  const resolveTerm = useCallback(
    (id: string) => {
      setQueue((q) =>
        q.map((r) => (r.id === id ? { ...r, status: "resolved" } : r)),
      );
      setStats((s) => ({ ...s, resolved: s.resolved + 1 }));
      toast("Term added to lexicon — model will retrain");
    },
    [toast],
  );

  const ignoreTerm = useCallback(
    (id: string) => {
      setQueue((q) =>
        q.map((r) => (r.id === id ? { ...r, status: "ignored" } : r)),
      );
      toast("Term ignored", "info");
    },
    [toast],
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
