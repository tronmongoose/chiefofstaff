"use client";

import Link from "next/link";
import WalletButton from "./WalletButton";

export function GlobalHeader() {
  return (
    <header className="w-full bg-white shadow-sm border-b border-gray-200 py-4 px-6">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">✈️</div>
          <div className="font-bold text-xl text-blue-700">Travel Planner</div>
        </div>
        <div className="flex items-center space-x-8">
          <nav className="flex items-center space-x-8">
            <Link 
              href="/" 
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200 relative group"
            >
              Home
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all duration-200 group-hover:w-full"></span>
            </Link>
            <Link 
              href="/review" 
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200 relative group"
            >
              Review
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all duration-200 group-hover:w-full"></span>
            </Link>
            <Link 
              href="/dashboard" 
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200 relative group"
            >
              Dashboard
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all duration-200 group-hover:w-full"></span>
            </Link>
            <Link 
              href="/reputation" 
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200 relative group"
            >
              Reputation
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all duration-200 group-hover:w-full"></span>
            </Link>
          </nav>
          <WalletButton />
        </div>
      </div>
    </header>
  );
} 