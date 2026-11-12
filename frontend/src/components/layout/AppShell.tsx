"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { PersistentNav } from "@/components/navigation/PersistentNav";
import { useLayoutContext } from "@/context/LayoutContext";

interface AppShellProps {
  children: React.ReactNode;
}

const NO_SIDEBAR_ROUTES = ["/login"];

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const { isSidebarHidden } = useLayoutContext();

  const isStandaloneRoute = NO_SIDEBAR_ROUTES.some((route) => pathname?.startsWith(route));
  const shouldHideSidebar = isStandaloneRoute || isSidebarHidden;

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col lg:flex-row">
      {!shouldHideSidebar && <PersistentNav />}
      <div className="flex-1 flex flex-col min-w-0">
        {children}
      </div>
    </div>
  );
}
