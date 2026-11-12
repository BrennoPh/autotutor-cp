import React from "react";
import { Terminal, HelpCircle, Layers, FileQuestion } from "lucide-react";
import { TutorActionType } from "@/types/tutor";
import { ContextualSelection } from "@/types/workspace";

interface ContextualPopoverProps {
  selection: ContextualSelection | null;
  onAction: (action: TutorActionType, text: string) => void;
  onClose: () => void;
}

export function ContextualPopover({ selection, onAction, onClose }: ContextualPopoverProps) {
  if (!selection || !selection.rangeRect) return null;

  const { rangeRect, text } = selection;
  const top = Math.max(10, rangeRect.top + window.scrollY - 44);
  const left = Math.max(16, Math.min(window.innerWidth - 340, rangeRect.left + window.scrollX + rangeRect.width / 2 - 160));

  const actions: { type: TutorActionType; label: string; icon: React.ElementType }[] = [
    { type: "explain_analogy", label: "Analogia", icon: Terminal },
    { type: "make_flashcard", label: "Flashcard", icon: Layers },
    { type: "simplify", label: "Simplificar", icon: HelpCircle },
    { type: "generate_quiz", label: "Desafio", icon: FileQuestion },
  ];

  return (
    <div
      role="toolbar"
      aria-label="Ações contextuais"
      style={{ top: `${top}px`, left: `${left}px` }}
      className="fixed z-50 flex items-center gap-1 p-1 bg-slate-900 text-slate-200 rounded-md shadow-lg border border-slate-800 animate-in fade-in zoom-in-95 duration-150"
    >
      <span className="text-[10px] uppercase font-mono font-medium tracking-wider text-slate-400 px-2 py-1 select-none flex items-center gap-1">
        <Terminal className="w-3 h-3 text-slate-500" />
        Ação
      </span>
      <div className="h-4 w-px bg-slate-800" />
      {actions.map((act) => {
        const Icon = act.icon;
        return (
          <button
            key={act.type}
            onClick={() => {
              onAction(act.type, text);
              onClose();
            }}
            className="flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-colors focus-visible:ring-1 focus-visible:ring-slate-400"
          >
            <Icon className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
            <span>{act.label}</span>
          </button>
        );
      })}
    </div>
  );
}
