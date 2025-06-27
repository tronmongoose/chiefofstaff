"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function ReviewPage() {
  const [plan, setPlan] = useState<any>(null);
  const [userWallet, setUserWallet] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const router = useRouter();

  useEffect(() => {
    // Try to load plan from localStorage (set by home page)
    const stored = localStorage.getItem("travelPlan");
    const wallet = localStorage.getItem("userWallet");
    if (stored) setPlan(JSON.parse(stored));
    if (wallet) setUserWallet(wallet);
  }, []);

  const handleConfirm = async () => {
    if (!plan?.plan_id || !userWallet) {
      setError("Missing plan or user wallet.");
      return;
    }
    setLoading(true);
    setError("");
    setConfirmation("");
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
        setConfirmation(data.confirmation_message);
        // Optionally, update plan status in localStorage
      } else {
        setError(data.error || "Failed to confirm plan.");
      }
    } catch (err: any) {
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  if (!plan) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center">No plan to review. <a href="/" className="text-blue-600 underline">Go Home</a></div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg p-8 mt-8">
        <h1 className="text-2xl font-bold mb-6 text-center">Review Your Plan</h1>
        <div className="mb-4">
          <div className="font-semibold">Destination:</div>
          <div>{plan.destination}</div>
        </div>
        <div className="mb-4">
          <div className="font-semibold">Flights:</div>
          <ul className="list-disc ml-6">
            {plan.flights.map((f: any, i: number) => (
              <li key={i}>{f.from_location} → {f.to_location} ({f.airline}, {f.dates}, ${f.price})</li>
            ))}
          </ul>
        </div>
        <div className="mb-4">
          <div className="font-semibold">Hotels:</div>
          <ul className="list-disc ml-6">
            {plan.hotels.map((h: any, i: number) => (
              <li key={i}>{h.name} in {h.location} (${h.price_per_night}/night × {h.nights} nights = ${h.total})</li>
            ))}
          </ul>
        </div>
        <div className="mb-4">
          <div className="font-semibold">Activities:</div>
          <ul className="list-disc ml-6">
            {plan.activities.map((a: string, i: number) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
        <div className="mb-4">
          <div className="font-semibold">Total Cost:</div>
          <div>${plan.total_cost.toLocaleString()}</div>
        </div>
        <div className="mb-4">
          <div className="font-semibold">Platform Fee:</div>
          <div>${plan.platform_fee.toLocaleString()}</div>
        </div>
        <div className="mb-4">
          <div className="font-semibold">Grand Total:</div>
          <div className="text-lg font-bold">${plan.grand_total.toLocaleString()}</div>
        </div>
        {error && <div className="mt-4 text-red-600 text-center">{error}</div>}
        {confirmation && <div className="mt-4 text-green-700 text-center whitespace-pre-line">{confirmation}</div>}
        <button
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition mt-6"
          onClick={handleConfirm}
          disabled={loading || !!confirmation}
        >
          {loading ? "Confirming..." : "Confirm Plan"}
        </button>
      </div>
    </main>
  );
} 