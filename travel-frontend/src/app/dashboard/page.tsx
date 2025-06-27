"use client";
import { useState } from "react";
import Link from "next/link";

export default function DashboardPage() {
  const [userWallet, setUserWallet] = useState("");
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchPlans = async () => {
    setLoading(true);
    setError("");
    setPlans([]);
    try {
      const res = await fetch(`http://localhost:8000/get_user_plans/${userWallet}`);
      const data = await res.json();
      if (data.status === "success") {
        setPlans(data.plans);
      } else {
        setError(data.error || "Failed to fetch plans.");
      }
    } catch (err: any) {
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg p-8 mt-8">
        <h1 className="text-2xl font-bold mb-6 text-center">User Dashboard</h1>
        <div className="flex flex-col sm:flex-row gap-2 mb-6">
          <input
            type="text"
            className="flex-1 border rounded px-3 py-2"
            value={userWallet}
            onChange={e => setUserWallet(e.target.value)}
            placeholder="Enter your wallet address"
          />
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
            onClick={fetchPlans}
            disabled={loading || !userWallet}
          >
            {loading ? "Loading..." : "Get My Plans"}
          </button>
        </div>
        {error && <div className="mb-4 text-red-600 text-center">{error}</div>}
        <div>
          {plans.length === 0 && !loading && <div className="text-gray-500 text-center">No plans found.</div>}
          {plans.length > 0 && (
            <ul className="divide-y">
              {plans.map((plan, i) => (
                <li key={plan.plan_id} className="py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="font-semibold">{plan.destination}</div>
                    <div className="text-sm text-gray-500">Created: {new Date(plan.created_at).toLocaleString()}</div>
                    <div className="text-sm">Status: <span className={plan.status === 'confirmed' ? 'text-green-600' : 'text-yellow-600'}>{plan.status}</span></div>
                  </div>
                  <div className="flex flex-col items-end mt-2 sm:mt-0">
                    <div className="font-bold text-lg">${plan.total_cost.toLocaleString()}</div>
                    {/* For now, just show plan_id. In a real app, link to /review or /plan/[id] */}
                    <Link href="/review">
                      <span className="text-blue-600 underline text-sm mt-1 cursor-pointer">View Details</span>
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </main>
  );
} 