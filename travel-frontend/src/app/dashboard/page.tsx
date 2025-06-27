"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { usePlan } from "../../context/PlanContext";

interface UserPlan {
  plan_id: string;
  destination: string;
  total_cost: number;
  created_at: string;
  status: string;
}

export default function DashboardPage() {
  const { userWallet, setPlan } = usePlan();
  const [plans, setPlans] = useState<UserPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    if (!userWallet) {
      router.push("/");
      return;
    }
    fetchUserPlans();
  }, [userWallet, router]);

  const fetchUserPlans = async () => {
    try {
      const res = await fetch(`http://localhost:8000/get_user_plans/${userWallet}`);
      const data = await res.json();
      if (data.status === "success") {
        setPlans(data.plans);
      } else {
        setError(data.error || "Failed to fetch plans");
      }
    } catch (err: any) {
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  const handleViewPlan = async (planId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/generate_plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destination: "Paris", // This would need to be retrieved from the plan details
          budget: 2000,
          user_wallet: userWallet,
        }),
      });
      const data = await res.json();
      if (data.status === "success") {
        setPlan(data.plan);
        router.push("/review");
      }
    } catch (err: any) {
      setError(err.message || "Failed to load plan details");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your travel plans...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Travel Dashboard</h1>
            <p className="text-gray-600">Manage and view your travel plans</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {plans.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">✈️</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">No Travel Plans Yet</h2>
              <p className="text-gray-600 mb-6">Start planning your next adventure!</p>
              <button
                onClick={() => router.push("/")}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-8 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                Create New Plan
              </button>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {plans.map((plan) => (
                <div key={plan.plan_id} className="bg-gray-50 rounded-xl p-6 hover:shadow-lg transition-all duration-200">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">{plan.destination}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      plan.status === 'confirmed' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {plan.status}
                    </span>
                  </div>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Total Cost:</span>
                      <span className="font-semibold text-green-600">${plan.total_cost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Created:</span>
                      <span className="text-gray-500">
                        {new Date(plan.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Plan ID:</span>
                      <span className="font-mono text-xs text-gray-500 truncate">
                        {plan.plan_id.slice(0, 8)}...
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <button
                      onClick={() => handleViewPlan(plan.plan_id)}
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-8 text-center">
            <button
              onClick={() => router.push("/")}
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 px-8 rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
            >
              Create New Plan
            </button>
          </div>
        </div>
      </div>
    </main>
  );
} 