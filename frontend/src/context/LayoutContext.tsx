"use client";

import React, { createContext, useContext, useState, useMemo } from "react";

export interface LayoutContextType {
  isSidebarHidden: boolean;
  setSidebarHidden: (hidden: boolean) => void;
}

const LayoutContext = createContext<LayoutContextType | undefined>(undefined);

export function LayoutProvider({ children }: { children: React.ReactNode }) {
  const [isSidebarHidden, setSidebarHidden] = useState(false);

  const value = useMemo<LayoutContextType>(
    () => ({
      isSidebarHidden,
      setSidebarHidden,
    }),
    [isSidebarHidden]
  );

  return <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>;
}

export function useLayoutContext(): LayoutContextType {
  const context = useContext(LayoutContext);
  if (!context) {
    return {
      isSidebarHidden: false,
      setSidebarHidden: () => {},
    };
  }
  return context;
}
