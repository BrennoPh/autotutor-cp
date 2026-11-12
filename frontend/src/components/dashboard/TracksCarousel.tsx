import React from "react";
import Link from "next/link";
import { ActiveTrack } from "@/types/dashboard";
import { Compass } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

interface TracksCarouselProps {
  tracks: ActiveTrack[];
  onSelectTrack: (trackId: string) => void;
}

export function TracksCarousel({ tracks, onSelectTrack }: TracksCarouselProps) {
  return (
    <section className="space-y-3" aria-labelledby="tracks-heading">
      <div className="flex items-center justify-between">
        <h2 id="tracks-heading" className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Compass className="w-3.5 h-3.5 text-blue-400" />
          <span>Trilhas em Andamento</span>
        </h2>
        <Link href="/trilhas" className="text-xs text-blue-400 hover:text-blue-300 font-medium transition-colors">
          Catálogo completo →
        </Link>
      </div>

      {tracks.length === 0 ? (
        <div className="p-6 rounded-xl border border-dashed border-border bg-card/40 backdrop-blur-sm text-center space-y-2">
          <p className="text-xs text-muted-foreground">Você ainda não possui nenhuma trilha ativa.</p>
          <Link
            href="/onboarding"
            className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline font-semibold"
          >
            <span>Fazer diagnóstico para calibrar trilha adaptativa</span>
            <span>→</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {tracks.map((track) => (
            <div
              key={track.id}
              onClick={() => onSelectTrack(track.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectTrack(track.id);
                }
              }}
              className="p-4 rounded-lg border border-slate-800 bg-slate-900/90 shadow-sm hover:border-slate-700 transition-colors duration-150 cursor-pointer flex flex-col justify-between space-y-3 group focus-visible:ring-1 focus-visible:ring-slate-400"
            >
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">
                    {track.subject}
                  </span>
                  <Badge variant={track.difficultyTag === "Iniciante" ? "secondary" : "primary"}>
                    {track.difficultyTag}
                  </Badge>
                </div>
                <h3 className="font-semibold text-sm text-slate-100 group-hover:text-blue-400 transition-colors">
                  {track.title}
                </h3>
              </div>

              <div className="space-y-2 pt-2 border-t border-slate-800/80">
                <div className="flex justify-between text-[11px] text-slate-400 font-mono">
                  <span>{track.completedModules} de {track.totalModules} módulos</span>
                  <span className="text-slate-300">{track.retentionRate}% retenção</span>
                </div>
                <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${(track.completedModules / track.totalModules) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
