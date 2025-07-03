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

  // Calculate x402 payment amounts
  const totalUSD = plan.grand_total;
  const x402Fee = 0.21; // Total x402 fees for the booking flow
  const totalUSDC = totalUSD + x402Fee;

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Hero Payment Section */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-6 border-2 border-blue-100">
          <div className="text-center mb-8">
            <div className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-blue-100 text-blue-800 mb-4">
              ⚡ x402 Crypto Payment Ready
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Pay with Crypto</h1>
            <p className="text-xl text-gray-600">Complete your booking with instant USDC payment</p>
          </div>

          {/* Payment Amount Display */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white mb-8">
            <div className="text-center">
              <div className="text-2xl font-medium mb-2">Total Payment</div>
              <div className="text-5xl font-bold mb-2">${totalUSD.toFixed(2)}</div>
              <div className="text-lg opacity-90">+ ${x402Fee.toFixed(2)} x402 fees</div>
              <div className="text-2xl font-semibold mt-2">= ${totalUSDC.toFixed(2)} USDC</div>
            </div>
          </div>

          {/* x402 Payment Benefits */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <div className="text-3xl mb-2">⚡</div>
              <h3 className="font-semibold mb-1">Instant</h3>
              <p className="text-sm text-gray-600">Payment confirmed in seconds</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🔒</div>
              <h3 className="font-semibold mb-1">Secure</h3>
              <p className="text-sm text-gray-600">Blockchain verified</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">💎</div>
              <h3 className="font-semibold mb-1">Transparent</h3>
              <p className="text-sm text-gray-600">No hidden fees</p>
            </div>
          </div>

          {/* Hero Action Button */}
          <div className="text-center">
            <button
              onClick={handleConfirm}
              disabled={loading}
              className="w-full max-w-md bg-gradient-to-r from-green-600 to-emerald-600 text-white py-6 px-8 rounded-2xl font-bold text-2xl hover:from-green-700 hover:to-emerald-700 transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-2xl"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                  Processing Payment...
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <span className="mr-2">💳</span>
                  Pay ${totalUSDC.toFixed(2)} USDC
                </div>
              )}
            </button>
            
            <p className="text-sm text-gray-500 mt-3">
              No credit card required • Instant confirmation • Secure blockchain payment
            </p>
          </div>
        </div>

        {/* Simplified Trip Summary */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Trip Summary</h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            {/* Basic Trip Info */}
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-blue-50 rounded-xl">
                <span className="font-medium">Destination</span>
                <span className="font-semibold text-blue-600">{plan.destination}</span>
              </div>
              
              <div className="flex justify-between items-center p-4 bg-green-50 rounded-xl">
                <span className="font-medium">Flights</span>
                <span className="font-semibold text-green-600">
                  ${plan.flights.reduce((sum: number, f: any) => sum + f.price, 0).toFixed(2)}
                </span>
              </div>
              
              <div className="flex justify-between items-center p-4 bg-purple-50 rounded-xl">
                <span className="font-medium">Accommodation</span>
                <span className="font-semibold text-purple-600">
                  ${plan.hotels.reduce((sum: number, h: any) => sum + h.total, 0).toFixed(2)}
                </span>
              </div>
            </div>

            {/* x402 Payment Breakdown */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">x402 Payment Breakdown</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Travel Cost:</span>
                  <span>${totalUSD.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-blue-600">
                  <span>Flight Search Fee:</span>
                  <span>0.01 USDC</span>
                </div>
                <div className="flex justify-between text-blue-600">
                  <span>Flight Booking Fee:</span>
                  <span>0.10 USDC</span>
                </div>
                <div className="flex justify-between text-blue-600">
                  <span>Hotel Booking Fee:</span>
                  <span>0.10 USDC</span>
                </div>
                <hr className="my-3" />
                <div className="flex justify-between font-bold text-lg">
                  <span>Total USDC:</span>
                  <span className="text-green-600">${totalUSDC.toFixed(2)}</span>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-blue-100 rounded-lg">
                <p className="text-sm text-blue-800">
                  💡 x402 fees are minimal and transparent. Traditional booking sites charge 10-20% in hidden fees.
                </p>
              </div>
            </div>
          </div>

          {/* Back Button */}
          <div className="text-center mt-8">
            <button
              onClick={() => router.push("/")}
              className="bg-gray-200 text-gray-700 py-3 px-8 rounded-xl font-semibold hover:bg-gray-300 transition-all duration-200"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>
    </main>
  );
} 