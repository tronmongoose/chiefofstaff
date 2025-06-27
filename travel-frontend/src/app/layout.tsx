import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import { PlanProvider } from "../context/PlanContext";
import { Suspense } from "react";
import { GlobalHeader } from "../components/GlobalHeader";
import { GlobalLoadingBar } from "../components/GlobalLoadingBar";
import { GlobalErrorAlert } from "../components/GlobalErrorAlert";

export const metadata: Metadata = {
  title: "Travel Planner",
  description: "Modern travel planning app",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="font-sans">
      <body className="bg-gray-50 min-h-screen font-sans">
        <PlanProvider>
          <GlobalHeader />
          <GlobalLoadingBar />
          <GlobalErrorAlert />
          <Suspense fallback={<div className="p-8 text-center">Loading...</div>}>
            {children}
          </Suspense>
        </PlanProvider>
      </body>
    </html>
  );
}
