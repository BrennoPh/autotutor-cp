"use client";

import React, { useState, useEffect, useTransition } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { usePathname } from "next/navigation";
import {
  Home,
  BookOpen,
  Network,
  Calendar,
  Brain,
  Cpu,
  Award,
  Compass,
  Settings,
  Library,
  BrainCircuit,
  LogIn,
  LogOut,
  Loader2,
  RotateCcw,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { apiRequest } from "@/services/apiClient";
import { purgeAllClientStudyData } from "@/hooks/useOnboardingGuard";

const AiConfigModal = dynamic(
  () => import("@/components/config/AiConfigModal").then((m) => m.AiConfigModal),
  { ssr: false }
);

interface PersistentNavProps {
  currentPath?: string;
  onNavigate?: (path: string) => void;
}

const NAV_ITEMS = [
  { label: "Início", path: "/", icon: Home },
  { label: "Trilhas de Estudo", path: "/trilhas", icon: Compass },
  { label: "Arena & Juiz", path: "/workspace", icon: BookOpen },
  { label: "Laboratório IA", path: "/lab", icon: BrainCircuit },
  { label: "Quadro Branco", path: "/whiteboard", icon: Network },
  { label: "Biblioteca & Aulas", path: "/biblioteca", icon: Library },
  { label: "Calendário", path: "/calendar", icon: Calendar },
  { label: "Repetição & Memória", path: "/repetition", icon: Brain },
  { label: "Diagnóstico", path: "/onboarding", icon: Award },
];

export function PersistentNav({ currentPath, onNavigate }: PersistentNavProps = {}) {
  const pathname = usePathname();
  const activePath = currentPath || pathname || "/";
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [pendingPath, setPendingPath] = useState<string | null>(null);
  const [, startTransition] = useTransition();
  const { user, isAuthenticated, logout } = useAuth();

  // Reset optimistic state when navigation resolves
  useEffect(() => {
    setPendingPath(null);
  }, [pathname]);

  // Safety fallback: if navigation takes longer than 1.8s, clear pending state to prevent infinite spinners
  useEffect(() => {
    if (!pendingPath) return;
    const timer = setTimeout(() => {
      setPendingPath(null);
    }, 1800);
    return () => clearTimeout(timer);
  }, [pendingPath]);

  // Global event listener to open AI configuration from anywhere in the app
  useEffect(() => {
    const handleOpenModal = () => setIsAiModalOpen(true);
    window.addEventListener("open-ai-config", handleOpenModal);
    return () => window.removeEventListener("open-ai-config", handleOpenModal);
  }, []);

  const handleLinkClick = (path: string) => {
    if (path !== activePath) {
      setPendingPath(path);
      if (onNavigate) {
        startTransition(() => {
          onNavigate(path);
        });
      }
    }
  };

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside
        aria-label="Navegação principal"
        className="hidden lg:flex flex-col w-64 border-r border-border bg-card/60 backdrop-blur-md p-4 h-screen sticky top-0 justify-between shrink-0 select-none overflow-y-auto"
      >
        <div className="space-y-6">
          <Link href="/" prefetch={true} className="flex items-center gap-2.5 px-2 group">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary font-mono font-bold text-sm group-hover:scale-105 transition-transform">
              &lt;/&gt;
            </div>
            <div>
              <span className="font-semibold text-sm tracking-tight block text-foreground">AutoTutor AI</span>
              <span className="text-[10px] text-muted-foreground uppercase font-medium tracking-wider">CP Platform</span>
            </div>
          </Link>

          <nav className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isCurrentActive =
                item.path === "/"
                  ? activePath === "/" || activePath === "/dashboard"
                  : activePath.startsWith(item.path);
              const isPending = pendingPath === item.path;
              const isHighlighted = isPending || isCurrentActive;

              return (
                <Link
                  key={item.path}
                  href={item.path}
                  prefetch={true}
                  onClick={() => handleLinkClick(item.path)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-100 ${
                    isHighlighted
                      ? "bg-primary text-primary-foreground shadow-sm ring-1 ring-primary/30"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                  }`}
                  aria-current={isCurrentActive ? "page" : undefined}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <Icon className="w-4 h-4 shrink-0" aria-hidden="true" />
                    <span className="truncate">{item.label}</span>
                  </div>
                  {isPending && (
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-primary-foreground shrink-0" aria-label="Carregando" />
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="space-y-2 pt-4 border-t border-border/40">
          {/* User Session Info */}
          {isAuthenticated && user ? (
            <div className="p-3 rounded-xl border border-border bg-secondary/40 flex items-center justify-between">
              <div className="flex items-center gap-2 min-w-0">
                <div className="w-7 h-7 rounded-lg bg-primary/20 text-primary flex items-center justify-center font-bold text-xs shrink-0">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="truncate">
                  <span className="text-xs font-bold text-foreground block truncate">{user.name}</span>
                  <span className="text-[10px] text-muted-foreground block truncate">@{user.username}</span>
                </div>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <button
                  type="button"
                  onClick={async () => {
                    if (confirm("Deseja realmente zerar todos os seus dados e recomeçar do zero?")) {
                      try {
                        await apiRequest("/api/progress/reset", { method: "POST" });
                      } catch (e) {
                        console.warn(e);
                      }
                      purgeAllClientStudyData();
                      window.location.href = "/onboarding";
                    }
                  }}
                  title="Zerar todos os dados e recomeçar do zero"
                  className="p-1.5 rounded-lg text-muted-foreground hover:text-amber-400 hover:bg-amber-500/10 transition-colors cursor-pointer"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={logout}
                  title="Sair da Conta"
                  className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors cursor-pointer"
                >
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ) : (
            <Link
              href="/login"
              prefetch={true}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold bg-primary/10 border border-primary/20 text-primary hover:bg-primary/20 transition-all"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Entrar / Cadastrar</span>
            </Link>
          )}

          {/* AI Settings Trigger at Bottom */}
          <button
            type="button"
            onClick={() => setIsAiModalOpen(true)}
            className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold border border-border bg-secondary/50 hover:bg-secondary text-foreground transition-all cursor-pointer group shadow-xs"
            title="Configurações de Provedores de IA (Gemini, Ollama, Chaves e Modelos)"
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <Cpu className="w-4 h-4 text-blue-400 shrink-0 group-hover:scale-110 transition-transform" />
              <span className="truncate font-semibold">Configurações de API</span>
            </div>
            <Settings className="w-3.5 h-3.5 text-muted-foreground group-hover:rotate-45 transition-transform" />
          </button>
        </div>
      </aside>

      {/* Mobile Bottom Navigation Bar */}
      <nav
        aria-label="Navegação móvel"
        className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-card/90 backdrop-blur-lg border-t border-border flex items-center justify-around py-2 px-1 select-none"
      >
        {NAV_ITEMS.slice(0, 5).map((item) => {
          const Icon = item.icon;
          const isCurrentActive =
            item.path === "/"
              ? activePath === "/" || activePath === "/dashboard"
              : activePath.startsWith(item.path);
          const isPending = pendingPath === item.path;
          const isHighlighted = isPending || isCurrentActive;

          return (
            <Link
              key={item.path}
              href={item.path}
              prefetch={true}
              onClick={() => handleLinkClick(item.path)}
              className={`flex flex-col items-center gap-1 py-1.5 px-2 rounded-lg text-[10px] min-w-[48px] min-h-[44px] transition-colors ${
                isHighlighted ? "text-primary font-bold" : "text-muted-foreground hover:text-foreground"
              }`}
              aria-current={isCurrentActive ? "page" : undefined}
            >
              {isPending ? (
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
              ) : (
                <Icon className="w-4 h-4" aria-hidden="true" />
              )}
              <span>{item.label.split(" ")[0]}</span>
            </Link>
          );
        })}
        <button
          type="button"
          onClick={() => setIsAiModalOpen(true)}
          className="flex flex-col items-center gap-1 py-1.5 px-2 rounded-lg text-[10px] min-w-[48px] min-h-[44px] text-muted-foreground hover:text-foreground cursor-pointer"
          title="Configurações de IA"
        >
          <Settings className="w-4 h-4 text-blue-400" />
          <span>Config IA</span>
        </button>
      </nav>

      {isAiModalOpen && <AiConfigModal isOpen={isAiModalOpen} onClose={() => setIsAiModalOpen(false)} />}
    </>
  );
}
