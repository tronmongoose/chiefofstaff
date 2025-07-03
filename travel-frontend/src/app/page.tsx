"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { usePlan } from "@/context/PlanContext";
import { useWallet } from "@/context/WalletContext";

export default function HomePage() {
  const [destination, setDestination] = useState("");
  const [budget, setBudget] = useState("");
  const router = useRouter();
  const { generatePlan, loading, error, setError } = usePlan();
  const { address, isConnected, connect } = useWallet();

  const handlePlanGeneration = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!destination || !budget) return;

    // Check if wallet is connected
    if (!isConnected || !address) {
      setError("Please connect your wallet first to generate a travel plan");
      return;
    }
    
    try {
      const success = await generatePlan(destination, parseFloat(budget), address);
      if (success) {
        router.push("/review");
      }
    } catch (error) {
      console.error("Error generating plan:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <div className="mb-8">
              <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-blue-100 text-blue-800 mb-4">
                🌟 World's First x402 Crypto-Payment Travel Booking
              </span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6">
              Travel the World with
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                {' '}Crypto
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto">
              Experience the future of travel booking with instant, secure payments using the revolutionary x402 standard. 
              No more credit cards, no more waiting - just seamless crypto payments.
            </p>

            {/* Primary Search Form - Front and Center */}
            <div className="max-w-4xl mx-auto mb-16">
              <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 p-8 md:p-12">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8 text-center">
                  Start Your Journey
                </h2>
                
                {/* Wallet Connection Status */}
                {!isConnected ? (
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 mb-6">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="text-2xl">🔗</div>
                      <h3 className="text-lg font-semibold text-amber-800">Connect Your Wallet</h3>
                    </div>
                    <p className="text-amber-700 mb-4">
                      Connect your Coinbase Wallet to start planning your trip with real blockchain integration.
                    </p>
                    <button
                      onClick={connect}
                      className="bg-amber-600 text-white px-6 py-3 rounded-xl hover:bg-amber-700 font-semibold"
                    >
                      Connect Wallet to Continue
                    </button>
                  </div>
                ) : (
                  <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="text-xl">✅</div>
                      <div>
                        <span className="text-green-800 font-semibold">Wallet Connected: </span>
                        <span className="text-green-700 font-mono text-sm">
                          {address?.slice(0, 6)}...{address?.slice(-4)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
                
                <form onSubmit={handlePlanGeneration} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="destination" className="block text-lg font-semibold text-gray-700 mb-3">
                        Where do you want to go?
                      </label>
                      <input
                        type="text"
                        id="destination"
                        value={destination}
                        onChange={(e) => setDestination(e.target.value)}
                        placeholder="e.g., Paris, Tokyo, New York"
                        className="w-full px-6 py-4 text-lg rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all"
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor="budget" className="block text-lg font-semibold text-gray-700 mb-3">
                        Budget (USD)
                      </label>
                      <input
                        type="number"
                        id="budget"
                        value={budget}
                        onChange={(e) => setBudget(e.target.value)}
                        placeholder="e.g., 2000"
                        className="w-full px-6 py-4 text-lg rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all"
                        required
                      />
                    </div>
                  </div>
                  
                  <button
                    type="submit"
                    disabled={loading || !isConnected}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-5 rounded-xl font-bold text-xl hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:transform-none shadow-lg"
                  >
                    {loading ? (
                      <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Creating Your Plan...
                      </span>
                    ) : !isConnected ? (
                      "🔗 Connect Wallet to Generate Plan"
                    ) : (
                      "🚀 Generate AI Travel Plan"
                    )}
                  </button>
                </form>
                
                {error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-700 text-sm">{error}</p>
                  </div>
                )}
                
                <p className="text-center text-gray-500 mt-4 text-sm">
                  Free plan generation • Crypto payments only for bookings
                </p>
              </div>
            </div>

            {/* Revolutionary Features */}
            <div className="grid md:grid-cols-3 gap-8 mb-12 max-w-4xl mx-auto">
              <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                <div className="text-3xl mb-4">⚡</div>
                <h3 className="text-lg font-semibold mb-2">Instant Payments</h3>
                <p className="text-gray-600">Pay with USDC in seconds, not days</p>
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                <div className="text-3xl mb-4">🔒</div>
                <h3 className="text-lg font-semibold mb-2">Secure & Transparent</h3>
                <p className="text-gray-600">Blockchain-powered security with full transparency</p>
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                <div className="text-3xl mb-4">🌍</div>
                <h3 className="text-lg font-semibold mb-2">Global Access</h3>
                <p className="text-gray-600">No borders, no restrictions, just travel</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">How x402 Travel Booking Works</h2>
            <p className="text-xl text-gray-600">Experience the revolutionary payment flow</p>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Plan Your Trip</h3>
              <p className="text-gray-600">AI-powered travel planning with real-time pricing</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">2</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Pay with Crypto</h3>
              <p className="text-gray-600">Instant USDC payments via x402 standard</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">3</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Instant Confirmation</h3>
              <p className="text-gray-600">Blockchain-verified booking confirmation</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">4</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Enjoy Your Trip</h3>
              <p className="text-gray-600">Travel with peace of mind</p>
            </div>
          </div>
        </div>
      </div>

      {/* x402 Technology Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Powered by x402 Standard</h2>
            <p className="text-xl text-gray-600">The revolutionary crypto payment protocol</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">What is x402?</h3>
              <p className="text-gray-600 mb-6">
                x402 is a revolutionary HTTP status code and payment standard that enables instant, 
                secure crypto payments for web services. It's the future of micro-payments and 
                subscription services.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  <span className="text-gray-700">Instant payment verification</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  <span className="text-gray-700">No third-party intermediaries</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  <span className="text-gray-700">Built-in security and transparency</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  <span className="text-gray-700">Global accessibility</span>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-8 shadow-lg">
              <h4 className="text-lg font-semibold mb-4">Payment Flow Example</h4>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <span>Flight Search</span>
                  <span className="text-green-600 font-mono">0.01 USDC</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <span>Flight Booking</span>
                  <span className="text-green-600 font-mono">0.10 USDC</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <span>Hotel Booking</span>
                  <span className="text-green-600 font-mono">0.10 USDC</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded font-semibold">
                  <span>Total Fees</span>
                  <span className="text-blue-600 font-mono">0.21 USDC</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4">x402 Travel Planner</h3>
            <p className="text-gray-400 mb-6">
              The future of travel booking is here. Experience seamless crypto payments.
            </p>
            <div className="flex justify-center space-x-6">
              <Link href="/dashboard" className="text-blue-400 hover:text-blue-300">
                Dashboard
              </Link>
              <a href="https://github.com/your-repo" className="text-blue-400 hover:text-blue-300">
                GitHub
              </a>
              <a href="/docs" className="text-blue-400 hover:text-blue-300">
                Documentation
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
