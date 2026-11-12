"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import {
  LogIn,
  UserPlus,
  KeyRound,
  User,
  Shield,
  ArrowRight,
  AlertCircle,
  Terminal,
  CheckCircle2,
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, register, isAuthenticated, user } = useAuth();

  const [tab, setTab] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<"student" | "teacher">("student");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsSubmitting(true);

    try {
      if (tab === "login") {
        await login(username, password);
        router.push("/dashboard");
      } else {
        await register({ username, name, password, role });
        // New user goes to onboarding to calibrate level
        router.push("/onboarding");
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Falha na autenticação. Verifique os dados informados.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center p-4 sm:p-6 relative overflow-hidden select-none">
      {/* Background Gradients */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-card/80 backdrop-blur-xl border border-border rounded-3xl shadow-2xl p-6 sm:p-8 space-y-6 relative z-10">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700/60 text-xs font-medium">
            <Terminal className="w-3.5 h-3.5 text-blue-400" />
            <span>AutoTutor CP • Plataforma de Treinamento</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
            {tab === "login" ? "Bem-vindo de volta" : "Crie sua Conta de Estudos"}
          </h1>
          <p className="text-xs text-muted-foreground">
            {tab === "login"
              ? "Acesse suas trilhas, submissões de código e progresso salvo."
              : "Inicie sua jornada personalizada em programação competitiva."}
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex bg-secondary/60 p-1 rounded-2xl border border-border">
          <button
            type="button"
            onClick={() => {
              setTab("login");
              setErrorMsg(null);
            }}
            className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-bold rounded-xl transition-all ${
              tab === "login"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>Entrar</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setTab("register");
              setErrorMsg(null);
            }}
            className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-bold rounded-xl transition-all ${
              tab === "register"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>Criar Conta</span>
          </button>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div className="p-3.5 rounded-xl border border-destructive/30 bg-destructive/10 text-destructive text-xs flex items-start gap-2.5 animate-in fade-in-0">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-semibold block">Erro</span>
              <p className="text-[11px] opacity-90 leading-relaxed">{errorMsg}</p>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {tab === "register" && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-muted-foreground" />
                <span>Nome Completo</span>
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="ex: Brenno Silva"
                className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-secondary/50 border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-muted-foreground" />
              <span>Nome de Usuário</span>
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value.toLowerCase().trim())}
              placeholder="ex: brenno_cp"
              className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-secondary/50 border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary font-mono"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
              <KeyRound className="w-3.5 h-3.5 text-muted-foreground" />
              <span>Senha de Acesso</span>
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              minLength={8}
              className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-secondary/50 border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary font-mono"
            />
          </div>

          {tab === "register" && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-muted-foreground" />
                <span>Perfil</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setRole("student")}
                  className={`px-3 py-2 rounded-xl text-xs font-semibold border transition-all ${
                    role === "student"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-secondary text-muted-foreground border-border hover:text-foreground"
                  }`}
                >
                  Aluno / Competidor
                </button>
                <button
                  type="button"
                  onClick={() => setRole("teacher")}
                  className={`px-3 py-2 rounded-xl text-xs font-semibold border transition-all ${
                    role === "teacher"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-secondary text-muted-foreground border-border hover:text-foreground"
                  }`}
                >
                  Instrutor / Coach
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-xs bg-primary text-primary-foreground hover:bg-primary-hover shadow-lg shadow-primary/25 transition-all active:scale-95 disabled:opacity-50"
          >
            <span>{isSubmitting ? "Autenticando..." : tab === "login" ? "Entrar na Plataforma" : "Cadastrar e Iniciar Diagnóstico"}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Guest Mode */}
        <div className="pt-2 border-t border-border/60 text-center">
          <button
            type="button"
            onClick={() => {
              document.cookie = "autotutor_token=guest_anonymous; path=/; max-age=86400; SameSite=Lax";
              router.push("/");
            }}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Continuar como Visitante (Sessão Anônima) →
          </button>
        </div>
      </div>
    </div>
  );
}
