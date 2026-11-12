"use client";

import React, { useEffect, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";

export function TopProgressBar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [progress, setProgress] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // When route changes, trigger a quick completion sweep
    setIsVisible(true);
    setProgress(30);

    const midTimer = setTimeout(() => {
      setProgress(85);
    }, 50);

    const finishTimer = setTimeout(() => {
      setProgress(100);
    }, 150);

    const hideTimer = setTimeout(() => {
      setIsVisible(false);
      setProgress(0);
    }, 400);

    return () => {
      clearTimeout(midTimer);
      clearTimeout(finishTimer);
      clearTimeout(hideTimer);
    };
  }, [pathname, searchParams]);

  if (!isVisible && progress === 0) return null;

  return (
    <div
      role="progressbar"
      aria-label="Indicador de navegação de página"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={progress}
      className="fixed top-0 left-0 right-0 z-50 pointer-events-none h-1 bg-transparent"
    >
      <div
        className="h-full bg-gradient-to-r from-primary via-primary/80 to-accent transition-all duration-200 ease-out shadow-sm"
        style={{
          width: `${progress}%`,
          opacity: isVisible ? 1 : 0,
        }}
      />
    </div>
  );
}
