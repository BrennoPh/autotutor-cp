import React from "react";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
  active?: boolean;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  return (
    <nav aria-label="Navegação estrutural" className="flex items-center text-xs text-muted-foreground py-2">
      <ol className="flex items-center gap-1.5 flex-wrap">
        <li>
          <Link
            href="/"
            prefetch={true}
            aria-label="Ir para a página inicial"
            className="flex items-center hover:text-foreground transition-colors p-1 rounded-sm focus-visible:ring-1 focus-visible:ring-primary"
          >
            <Home className="w-3.5 h-3.5" />
          </Link>
        </li>
        {items.map((item, index) => (
          <li key={index} className="flex items-center gap-1.5">
            <ChevronRight className="w-3 h-3 text-muted-foreground/60" aria-hidden="true" />
            {item.active ? (
              <span className="font-semibold text-foreground" aria-current="page">
                {item.label}
              </span>
            ) : item.href ? (
              <Link
                href={item.href}
                prefetch={true}
                className="hover:text-foreground transition-colors p-0.5 rounded-sm focus-visible:ring-1 focus-visible:ring-primary"
              >
                {item.label}
              </Link>
            ) : (
              <span>{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
