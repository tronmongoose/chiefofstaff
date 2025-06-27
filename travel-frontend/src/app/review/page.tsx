"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { usePlan } from "../../context/PlanContext";

export default function ReviewPage() {
  const { plan, userWallet, confirmPlan, loading } = usePlan();
  const router = useRouter();

  useEffect(() => {
    if (!plan) {
      router.push("/");
    }
  }, [plan, router]);

  const handleConfirm = async () => {
    const success = await confirmPlan();
    if (success) {
      router.push("/dashboard");
    }
  };

  if (!plan) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading plan...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Review Your Travel Plan</h1>
            <p className="text-gray-600">Please review your trip details before confirming</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Plan Summary */}
            <div className="space-y-6">
              <div className="bg-blue-50 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Trip Summary</h2>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Destination:</span>
                    <span className="font-semibold">{plan.destination}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Cost:</span>
                    <span className="font-semibold text-green-600">${plan.grand_total.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Plan ID:</span>
                    <span className="font-mono text-sm text-gray-500">{plan.plan_id}</span>
                  </div>
                </div>
              </div>

              {/* Flights */}
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">✈️ Flights</h3>
                {plan.flights.map((flight: any, index: number) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-4 mb-4">
                    <div className="font-medium">{flight.from_location} → {flight.to_location}</div>
                    <div className="text-sm text-gray-600">{flight.airline}</div>
                    <div className="text-sm text-gray-600">{flight.dates}</div>
                    <div className="text-green-600 font-semibold">${flight.price.toFixed(2)}</div>
                  </div>
                ))}
              </div>

              {/* Hotels */}
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🏨 Accommodation</h3>
                {plan.hotels.map((hotel: any, index: number) => (
                  <div key={index} className="border-l-4 border-green-500 pl-4 mb-4">
                    <div className="font-medium">{hotel.name}</div>
                    <div className="text-sm text-gray-600">{hotel.location}</div>
                    <div className="text-sm text-gray-600">{hotel.nights} nights × ${hotel.price_per_night.toFixed(2)}</div>
                    <div className="text-green-600 font-semibold">${hotel.total.toFixed(2)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Activities and Actions */}
            <div className="space-y-6">
              {/* Activities */}
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Activities</h3>
                <ul className="space-y-2">
                  {plan.activities.map((activity: string, index: number) => (
                    <li key={index} className="flex items-center">
                      <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                      {activity}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Cost Breakdown */}
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">💰 Cost Breakdown</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Flights:</span>
                    <span>${plan.flights.reduce((sum: number, f: any) => sum + f.price, 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Accommodation:</span>
                    <span>${plan.hotels.reduce((sum: number, h: any) => sum + h.total, 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Activities:</span>
                    <span>$200.00</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Platform Fee:</span>
                    <span>${plan.platform_fee.toFixed(2)}</span>
                  </div>
                  <hr className="my-2" />
                  <div className="flex justify-between font-semibold text-lg">
                    <span>Total:</span>
                    <span className="text-green-600">${plan.grand_total.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-4">
                <button
                  onClick={handleConfirm}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
                >
                  {loading ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Confirming...
                    </div>
                  ) : (
                    "Confirm & Book Trip"
                  )}
                </button>
                
                <button
                  onClick={() => router.push("/")}
                  className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-xl font-semibold hover:bg-gray-300 transition-all duration-200"
                >
                  Back to Home
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
} 