import React from "react";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "ai" | "muted" | "success" | "warning" | "danger";
  className?: string;
}

export function Badge({ children, variant = "secondary", className = "" }: BadgeProps) {
  const variantStyles = {
    primary: "bg-blue-950/60 text-blue-400 border-blue-800/60 font-medium",
    secondary: "bg-slate-800 text-slate-300 border-slate-700/60",
    ai: "bg-slate-800 text-slate-300 border-slate-700 font-medium",
    muted: "bg-slate-900 text-slate-400 border-slate-800",
    success: "bg-emerald-950/60 text-emerald-400 border-emerald-800/60 font-medium",
    warning: "bg-amber-950/60 text-amber-400 border-amber-800/60 font-medium",
    danger: "bg-red-950/60 text-red-400 border-red-800/60 font-medium",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] border ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
