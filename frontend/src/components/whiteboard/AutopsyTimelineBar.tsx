"use client";

import React from "react";
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  RotateCcw,
  AlertOctagon,
  History,
  Zap,
} from "lucide-react";
import { PlaybackStatus } from "@/types/graphLab";

export interface AutopsyTimelineBarProps {
  currentStepIndex: number;
  totalSteps: number;
  playbackStatus: PlaybackStatus;
  failureStep?: number | null;
  failureReason?: string | null;
  currentExplanation?: string;
  currentEvent?: string;
  speedMs: number;
  onStepChange: (index: number) => void;
  onPlayPause: () => void;
  onReset: () => void;
  onSpeedChange: (speed: number) => void;
  className?: string;
}

export const AutopsyTimelineBar: React.FC<AutopsyTimelineBarProps> = ({
  currentStepIndex,
  totalSteps,
  playbackStatus,
  failureStep,
  failureReason,
  currentExplanation,
  currentEvent,
  speedMs,
  onStepChange,
  onPlayPause,
  onReset,
  onSpeedChange,
  className = "",
}) => {
  const isDeadPoint = failureStep !== null && failureStep !== undefined && currentStepIndex === failureStep;
  const hasDeathPoint = failureStep !== null && failureStep !== undefined && totalSteps > 0;
  const progressPercent = totalSteps > 0 ? (currentStepIndex / (totalSteps - 1 || 1)) * 100 : 0;
  const deathPointPercent = hasDeathPoint ? (failureStep / (totalSteps - 1 || 1)) * 100 : null;

  return (
    <div
      role="region"
      aria-label="Controle Temporal da Autópsia Algorítmica"
      className={`rounded-2xl border border-slate-800 bg-slate-950/90 p-4 shadow-lg backdrop-blur-md transition-all duration-150 ${className}`}
    >
      {/* Top Header: Metadata & Jump to Death Point */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
            <History className="h-4 w-4" />
          </div>
          <div>
            <span className="text-xs font-semibold tracking-wide text-slate-100">
              Autópsia Temporal (Time Machine)
            </span>
            <span className="ml-2 font-mono text-[11px] text-slate-400">
              Passo {totalSteps > 0 ? currentStepIndex + 1 : 0} de {totalSteps}
            </span>
          </div>
        </div>

        {hasDeathPoint && (
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 rounded-full border border-rose-500/30 bg-rose-500/10 px-2.5 py-0.5 text-[11px] font-medium text-rose-400">
              <AlertOctagon className="h-3 w-3" />
              Ponto de Morte: Passo {failureStep + 1}
            </span>

            <button
              type="button"
              onClick={() => onStepChange(failureStep)}
              aria-label="Saltar diretamente para o ponto de morte"
              className="flex items-center gap-1 rounded-lg bg-rose-600/90 hover:bg-rose-500 px-2.5 py-1 text-[11px] font-bold text-white shadow-sm transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400 active:scale-95"
            >
              <Zap className="h-3 w-3 fill-current" />
              <span>Ir para o Ponto de Falha</span>
            </button>
          </div>
        )}
      </div>

      {/* Scrubber & Timeline Track */}
      <div className="pt-3 pb-2 space-y-1.5">
        <div className="relative flex items-center h-4">
          {/* Base track */}
          <div className="absolute inset-x-0 h-2 rounded-full bg-slate-900 border border-slate-800/80 overflow-hidden">
            <div
              className={`h-full transition-all duration-75 ${
                isDeadPoint ? "bg-rose-500" : "bg-gradient-to-r from-indigo-600 to-indigo-500"
              }`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          {/* Marker of Death Point on track */}
          {deathPointPercent !== null && (
            <div
              className="absolute top-1/2 -translate-y-1/2 w-2 h-4 bg-rose-500 rounded-sm shadow-md shadow-rose-500/50 z-10 pointer-events-none"
              style={{ left: `calc(${deathPointPercent}% - 4px)` }}
              title={`Ponto de falha no passo ${failureStep! + 1}`}
            />
          )}

          {/* Interactive Range Input */}
          <input
            type="range"
            min={0}
            max={Math.max(0, totalSteps - 1)}
            value={currentStepIndex}
            onChange={(e) => onStepChange(Number(e.target.value))}
            aria-label="Arrastar posição na fita temporal"
            className="absolute inset-x-0 w-full opacity-0 cursor-pointer h-5 z-20"
          />
        </div>
      </div>

      {/* Frame Explanation Pill */}
      {currentExplanation && (
        <div
          className={`rounded-xl px-3 py-2 text-xs leading-relaxed transition-colors border ${
            isDeadPoint
              ? "border-rose-500/40 bg-rose-950/20 text-rose-300"
              : "border-slate-800 bg-slate-900/60 text-slate-300"
          }`}
        >
          <div className="flex items-center gap-2">
            <span
              className={`font-mono text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                isDeadPoint
                  ? "bg-rose-500/20 text-rose-400"
                  : "bg-indigo-500/20 text-indigo-300"
              }`}
            >
              {currentEvent || "EXEC"}
            </span>
            <span className="truncate">{currentExplanation}</span>
          </div>
          {isDeadPoint && failureReason && (
            <p className="mt-1 text-[11px] font-medium text-rose-400 border-t border-rose-500/20 pt-1">
              ⚠️ Causa do colapso: {failureReason}
            </p>
          )}
        </div>
      )}

      {/* Playback Controls & Speed Options */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-3">
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={onReset}
            aria-label="Reiniciar do primeiro passo"
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-colors"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>

          <button
            type="button"
            onClick={() => onStepChange(Math.max(0, currentStepIndex - 1))}
            disabled={currentStepIndex === 0}
            aria-label="Passo anterior"
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-colors"
          >
            <SkipBack className="h-3.5 w-3.5" />
          </button>

          <button
            type="button"
            onClick={onPlayPause}
            aria-label={playbackStatus === "playing" ? "Pausar reprodução" : "Iniciar reprodução"}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold text-xs bg-indigo-600 text-white hover:bg-indigo-500 shadow-sm transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 active:scale-95"
          >
            {playbackStatus === "playing" ? (
              <>
                <Pause className="h-3.5 w-3.5 fill-current" />
                <span>Pausar</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>Reproduzir</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => onStepChange(Math.min(totalSteps - 1, currentStepIndex + 1))}
            disabled={currentStepIndex >= totalSteps - 1}
            aria-label="Próximo passo"
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-colors"
          >
            <SkipForward className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Speed presets */}
        <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          {[
            { label: "0.5x", value: 1000 },
            { label: "1x", value: 600 },
            { label: "2x", value: 250 },
          ].map((item) => (
            <button
              key={item.label}
              type="button"
              onClick={() => onSpeedChange(item.value)}
              className={`px-2 py-0.5 rounded-lg text-[10px] font-mono font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${
                speedMs === item.value
                  ? "bg-indigo-600 text-white shadow-xs"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
