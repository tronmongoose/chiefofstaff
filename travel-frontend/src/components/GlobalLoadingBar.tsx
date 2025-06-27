"use client";

import { usePlan } from "../context/PlanContext";

export function GlobalLoadingBar() {
  const { loading } = usePlan();
  return loading ? (
    <div className="fixed top-0 left-0 w-full h-1 bg-blue-500 animate-pulse z-50" />
  ) : null;
} 