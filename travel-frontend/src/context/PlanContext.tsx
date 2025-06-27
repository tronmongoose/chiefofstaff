"use client";
import React, { createContext, useContext, useState, useEffect } from "react";

interface PlanContextType {
  plan: any;
  setPlan: (plan: any) => void;
  userWallet: string;
  setUserWallet: (wallet: string) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
  error: string;
  setError: (error: string) => void;
  generatePlan: (destination: string, budget: number, wallet: string) => Promise<boolean>;
  confirmPlan: () => Promise<boolean>;
}

const PlanContext = createContext<PlanContextType | undefined>(undefined);

export const PlanProvider = ({ children }: { children: React.ReactNode }) => {
  const [plan, setPlanState] = useState<any>(null);
  const [userWallet, setUserWalletState] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Persist plan and wallet in localStorage
  useEffect(() => {
    const storedPlan = localStorage.getItem("travelPlan");
    const storedWallet = localStorage.getItem("userWallet");
    if (storedPlan) setPlanState(JSON.parse(storedPlan));
    if (storedWallet) setUserWalletState(storedWallet);
  }, []);

  useEffect(() => {
    if (plan) {
      localStorage.setItem("travelPlan", JSON.stringify(plan));
    } else {
      localStorage.removeItem("travelPlan");
    }
  }, [plan]);

  useEffect(() => {
    if (userWallet) {
      localStorage.setItem("userWallet", userWallet);
    } else {
      localStorage.removeItem("userWallet");
    }
  }, [userWallet]);

  const setPlan = (p: any) => setPlanState(p);
  const setUserWallet = (w: string) => setUserWalletState(w);

  const generatePlan = async (destination: string, budget: number, wallet: string): Promise<boolean> => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/generate_plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destination,
          budget,
          user_wallet: wallet,
        }),
      });
      const data = await res.json();
      if (data.status === "success") {
        setPlan(data.plan);
        setUserWallet(wallet);
        return true;
      } else {
        setError(data.error || "Failed to generate plan.");
        return false;
      }
    } catch (err: any) {
      setError(err.message || "Network error");
      return false;
    } finally {
      setLoading(false);
    }
  };

  const confirmPlan = async (): Promise<boolean> => {
    if (!plan?.plan_id || !userWallet) {
      setError("Missing plan or user wallet.");
      return false;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/confirm_plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan_id: plan.plan_id,
          user_wallet: userWallet,
        }),
      });
      const data = await res.json();
      if (data.status === "success") {
        return true;
      } else {
        setError(data.error || "Failed to confirm plan.");
        return false;
      }
    } catch (err: any) {
      setError(err.message || "Network error");
      return false;
    } finally {
      setLoading(false);
    }
  };

  return (
    <PlanContext.Provider value={{ 
      plan, 
      setPlan, 
      userWallet, 
      setUserWallet, 
      loading, 
      setLoading, 
      error, 
      setError,
      generatePlan,
      confirmPlan
    }}>
      {children}
    </PlanContext.Provider>
  );
};

export const usePlan = () => {
  const ctx = useContext(PlanContext);
  if (!ctx) throw new Error("usePlan must be used within a PlanProvider");
  return ctx;
}; 