import React from "react";
import { Sparkles, ArrowRight, Target, Clock, BookOpen } from "lucide-react";

interface FirstDayHeroCardProps {
  onStart: () => void;
}

export function FirstDayHeroCard({ onStart }: FirstDayHeroCardProps) {
  return (
    <section
      aria-label="Boas-vindas ao AutoTutor CP"
      className="p-6 sm:p-8 rounded-xl border border-slate-800 bg-slate-900 shadow-sm space-y-6"
    >
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-3 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Primeiro Acesso • Bem-vindo</span>
          </div>

          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-100">
            Bem-vindo ao AutoTutor CP!
          </h1>

          <p className="text-sm text-slate-300 leading-relaxed">
            Bem-vindo ao AutoTutor CP. Vamos mapear seu nível e criar sua trilha personalizada em menos de 3 minutos.
          </p>

          <p className="text-xs text-slate-400 leading-relaxed">
            Seu ambiente de estudo personalizado está pronto para ser configurado. Faça o teste de nivelamento rápido para calibrar suas primeiras trilhas e seu cronograma semanal.
          </p>
        </div>

        <div className="shrink-0 w-full sm:w-auto flex flex-col sm:items-end gap-2">
          <button
            onClick={onStart}
            aria-label="Iniciar Diagnóstico Rápido"
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-3 rounded-md font-medium text-xs sm:text-sm bg-blue-600 text-white hover:bg-blue-500 shadow-md transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-slate-900 group"
          >
            <span>Iniciar Diagnóstico Rápido</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </button>
          <span className="text-[11px] text-slate-500 font-mono text-center sm:text-right">
            ⏱️ 5 questões práticas • Sem pressão
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 border-t border-slate-800/80">
        <div className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-800/40 border border-slate-800/60">
          <Target className="w-4 h-4 text-blue-400 shrink-0" />
          <span className="text-xs text-slate-300 font-medium">Diagnóstico Adaptativo</span>
        </div>
        <div className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-800/40 border border-slate-800/60">
          <BookOpen className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="text-xs text-slate-300 font-medium">Trilha Customizada</span>
        </div>
        <div className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-800/40 border border-slate-800/60">
          <Clock className="w-4 h-4 text-purple-400 shrink-0" />
          <span className="text-xs text-slate-300 font-medium">Cronograma Semanal</span>
        </div>
      </div>
    </section>
  );
}
