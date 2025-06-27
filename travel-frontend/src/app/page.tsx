"use client";
import { useState } from "react";

export default function Home() {
  const [destination, setDestination] = useState("");
  const [budget, setBudget] = useState("");
  const [userWallet, setUserWallet] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [plan, setPlan] = useState<any>(null);
  const [formattedPlan, setFormattedPlan] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setPlan(null);
    setFormattedPlan("");
    try {
      const res = await fetch("http://localhost:8000/generate_plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destination,
          budget: parseFloat(budget),
          user_wallet: userWallet,
        }),
      });
      const data = await res.json();
      if (data.status === "success") {
        setPlan(data.plan);
        setFormattedPlan(data.formatted_plan);
      } else {
        setError(data.error || "Failed to generate plan.");
      }
    } catch (err: any) {
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-8 mt-8">
        <h1 className="text-2xl font-bold mb-6 text-center">Travel Planner</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Destination</label>
            <input
              type="text"
              className="w-full border rounded px-3 py-2"
              value={destination}
              onChange={e => setDestination(e.target.value)}
              required
              placeholder="e.g. Paris"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Budget (USD)</label>
            <input
              type="number"
              className="w-full border rounded px-3 py-2"
              value={budget}
              onChange={e => setBudget(e.target.value)}
              required
              min={1}
              placeholder="e.g. 2000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">User Wallet</label>
            <input
              type="text"
              className="w-full border rounded px-3 py-2"
              value={userWallet}
              onChange={e => setUserWallet(e.target.value)}
              required
              placeholder="e.g. 0x123..."
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Plan"}
          </button>
        </form>
        {error && <div className="mt-4 text-red-600 text-center">{error}</div>}
        {formattedPlan && (
          <div className="mt-8 p-4 bg-gray-100 rounded overflow-x-auto prose prose-sm max-w-none">
            <h2 className="text-lg font-semibold mb-2">Your Travel Plan</h2>
            <div dangerouslySetInnerHTML={{ __html: formattedPlan.replace(/\n/g, '<br/>') }} />
          </div>
        )}
      </div>
    </main>
  );
}
