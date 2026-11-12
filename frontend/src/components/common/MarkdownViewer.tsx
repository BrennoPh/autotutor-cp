import dynamic from "next/dynamic";
import type { MarkdownRendererProps } from "@/components/ui/MarkdownRenderer";

export type { MarkdownRendererProps as MarkdownViewerProps };

export const MarkdownViewer = dynamic<MarkdownRendererProps>(
  () => import("@/components/ui/MarkdownRenderer").then((m) => m.MarkdownRenderer),
  {
    ssr: false,
    loading: () => (
      <div className="space-y-2 py-2 animate-pulse" aria-hidden="true">
        <div className="h-4 bg-muted/60 rounded w-3/4" />
        <div className="h-4 bg-muted/40 rounded w-5/6" />
        <div className="h-4 bg-muted/50 rounded w-2/3" />
      </div>
    ),
  }
);

export const MarkdownRenderer = MarkdownViewer;
export default MarkdownViewer;
