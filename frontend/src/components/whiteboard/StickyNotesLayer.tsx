"use client";

import React, { useState, useRef } from "react";
import { StickyNote, StickyColor } from "@/types/whiteboard";
import { X, GripVertical, Palette } from "lucide-react";

interface StickyNotesLayerProps {
  notes: StickyNote[];
  onUpdateNote: (id: string, updates: Partial<StickyNote>) => void;
  onDeleteNote: (id: string) => void;
}

const COLOR_CLASSES: Record<StickyColor, { bg: string; border: string; text: string; shadow: string }> = {
  yellow: {
    bg: "bg-amber-100 dark:bg-amber-950/90",
    border: "border-amber-300 dark:border-amber-800",
    text: "text-amber-950 dark:text-amber-100",
    shadow: "shadow-amber-500/10",
  },
  cyan: {
    bg: "bg-sky-100 dark:bg-sky-950/90",
    border: "border-sky-300 dark:border-sky-800",
    text: "text-sky-950 dark:text-sky-100",
    shadow: "shadow-sky-500/10",
  },
  green: {
    bg: "bg-emerald-100 dark:bg-emerald-950/90",
    border: "border-emerald-300 dark:border-emerald-800",
    text: "text-emerald-950 dark:text-emerald-100",
    shadow: "shadow-emerald-500/10",
  },
  pink: {
    bg: "bg-rose-100 dark:bg-rose-950/90",
    border: "border-rose-300 dark:border-rose-800",
    text: "text-rose-950 dark:text-rose-100",
    shadow: "shadow-rose-500/10",
  },
  orange: {
    bg: "bg-orange-100 dark:bg-orange-950/90",
    border: "border-orange-300 dark:border-orange-800",
    text: "text-orange-950 dark:text-orange-100",
    shadow: "shadow-orange-500/10",
  },
};

const COLOR_LIST: StickyColor[] = ["yellow", "cyan", "green", "pink", "orange"];

export function StickyNotesLayer({
  notes,
  onUpdateNote,
  onDeleteNote,
}: StickyNotesLayerProps) {
  const [activeDragId, setActiveDragId] = useState<string | null>(null);
  const dragOffsetRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const handlePointerDown = (e: React.PointerEvent, note: StickyNote) => {
    setActiveDragId(note.id);
    dragOffsetRef.current = {
      x: e.clientX - note.x,
      y: e.clientY - note.y,
    };
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent, note: StickyNote) => {
    if (activeDragId !== note.id) return;
    const newX = Math.max(10, e.clientX - dragOffsetRef.current.x);
    const newY = Math.max(10, e.clientY - dragOffsetRef.current.y);
    onUpdateNote(note.id, { x: newX, y: newY });
  };

  const handlePointerUp = (e: React.PointerEvent, note: StickyNote) => {
    if (activeDragId === note.id) {
      setActiveDragId(null);
      try {
        (e.target as HTMLElement).releasePointerCapture(e.pointerId);
      } catch {
        // Safe ignore
      }
    }
  };

  const cycleColor = (note: StickyNote) => {
    const currentIdx = COLOR_LIST.indexOf(note.color);
    const nextColor = COLOR_LIST[(currentIdx + 1) % COLOR_LIST.length];
    onUpdateNote(note.id, { color: nextColor });
  };

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden z-20">
      {notes.map((note) => {
        const theme = COLOR_CLASSES[note.color] || COLOR_CLASSES.yellow;

        return (
          <div
            key={note.id}
            style={{
              position: "absolute",
              left: `${note.x}px`,
              top: `${note.y}px`,
              width: `${note.width || 210}px`,
            }}
            className={`pointer-events-auto rounded-xl border p-2.5 shadow-md flex flex-col gap-1.5 transition-shadow ${theme.bg} ${theme.border} ${theme.shadow} backdrop-blur-xs`}
          >
            {/* Header: Drag Handle, Color Cycle & Delete */}
            <div className="flex items-center justify-between cursor-move select-none border-b border-black/10 dark:border-white/10 pb-1">
              <div
                className="flex items-center gap-1 text-xs opacity-60 hover:opacity-100"
                onPointerDown={(e) => handlePointerDown(e, note)}
                onPointerMove={(e) => handlePointerMove(e, note)}
                onPointerUp={(e) => handlePointerUp(e, note)}
              >
                <GripVertical className="w-3.5 h-3.5" />
                <span className="text-[10px] font-semibold uppercase tracking-wider">Post-it</span>
              </div>

              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => cycleColor(note)}
                  title="Alterar cor do Post-it"
                  className="p-1 rounded-md opacity-60 hover:opacity-100 hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
                >
                  <Palette className="w-3 h-3" />
                </button>
                <button
                  type="button"
                  onClick={() => onDeleteNote(note.id)}
                  title="Excluir post-it"
                  className="p-1 rounded-md opacity-60 hover:opacity-100 hover:text-red-500 hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>

            {/* Note Text Area */}
            <textarea
              value={note.text}
              onChange={(e) => onUpdateNote(note.id, { text: e.target.value })}
              placeholder="Digite sua anotação ou invariante aqui..."
              rows={4}
              className={`w-full bg-transparent resize-none focus:outline-none text-xs font-sans leading-relaxed selection:bg-black/20 dark:selection:bg-white/20 ${theme.text}`}
            />
          </div>
        );
      })}
    </div>
  );
}
