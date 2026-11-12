import React, { Suspense } from "react";
import "@/styles/globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { LayoutProvider } from "@/context/LayoutContext";
import { TopProgressBar } from "@/components/ui/TopProgressBar";
import { AppShell } from "@/components/layout/AppShell";

export const metadata = {
  title: "AutoTutor AI · Competitive Programming & EdTech Platform",
  description: "Plataforma de aprendizado adaptativo orientada por IA com laboratório interativo de grafos e juiz online.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="min-h-screen bg-background text-foreground antialiased font-sans selection:bg-primary/20 selection:text-primary">
        <AuthProvider>
          <LayoutProvider>
            <Suspense fallback={null}>
              <TopProgressBar />
            </Suspense>
            <AppShell>{children}</AppShell>
          </LayoutProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
