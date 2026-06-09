import type { Metadata } from "next";
import "./globals.css";
import { AppProvider } from "@/context/AppContext";
import { ClientShell } from "@/components/ClientShell";

export const metadata: Metadata = {
  title: "Protocol 67 — Brainrot to English",
  description: "Agent-driven internet slang translation and sentiment analysis system",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProvider>
          <ClientShell>{children}</ClientShell>
        </AppProvider>
      </body>
    </html>
  );
}
