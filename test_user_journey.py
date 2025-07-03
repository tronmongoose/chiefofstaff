#!/usr/bin/env python3
"""
Comprehensive end-to-end user journey test for the Travel Planning System.
Tests the complete flow: Plan → Search → Book → Confirm with x402 payments.
"""

import requests
import json
import time
import psycopg2
from datetime import datetime
from typing import Dict, Any, Optional

class UserJourneyTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.booking_id = None
        self.plan_id = None
        self.user_wallet = "0x1234567890abcdef1234567890abcdef12345678"

    def run_complete_journey(self):
        """Test complete user journey: Plan → Search → Book → Confirm"""
        print("🚀 TESTING COMPLETE USER JOURNEY")
        print("=" * 60)

        # Step 1: Create travel plan (free)
        self.create_travel_plan()

        # Step 2: Search flights (0.01 USDC)
        self.search_flights_with_payment()

        # Step 3: Book flight (0.10 USDC)
        self.book_flight_with_payment()

        # Step 4: Check booking status
        if self.booking_id:
            self.check_booking_status()

        # Step 5: Calculate total costs
        self.calculate_total_costs()

        # Step 6: Check database
        self.verify_database_records()

        print("\n🎉 COMPLETE USER JOURNEY TEST FINISHED!")

    def simulate_realistic_payment(self, amount: str) -> Dict[str, Any]:
        """Create realistic payment header with proper format"""
        wallet_address = "0xd4B1EB29143A6435E76FbE258Fb788bCb67EC8dD"  # Payment wallet from backend
        return {
            "transactionHash": f"0x{'f' * 60}{int(time.time()) % 1000:03d}",
            "amount": amount,
            "currency": "USDC",
            "recipient": wallet_address,
            "network": "base-mainnet",
            "chainId": 8453,
            "timestamp": int(time.time()),
            "verified": True  # Simulate successful verification
        }

    def create_travel_plan(self):
        """Step 1: Create a travel plan (free)"""
        print("\n📋 Step 1: Creating travel plan (FREE)...")
        
        try:
            response = requests.post(f"{self.base_url}/generate_plan", json={
                "destination": "Paris",
                "budget": 3000.0,
                "user_wallet": self.user_wallet,
                "session_id": f"test-session-{int(time.time())}"
            })

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    plan = data.get('plan', {})
                    self.plan_id = plan.get('plan_id')
                    print(f"   ✅ Plan created for {plan.get('destination', 'Unknown')}")
                    print(f"   💰 Estimated cost: ${plan.get('total_cost', 'N/A')}")
                    print(f"   🆔 Plan ID: {self.plan_id}")
                else:
                    print(f"   ❌ Plan creation failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Plan creation failed: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception in plan creation: {e}")

    def search_flights_with_payment(self):
        """Step 2: Search flights with payment (0.01 USDC)"""
        print("\n🔍 Step 2: Searching flights (0.01 USDC payment)...")

        try:
            # First try without payment (should get 402)
            response = requests.get(f"{self.base_url}/api/flights/search", params={
                "origin": "JFK", "destination": "CDG", "date": "2024-08-01"
            })

            if response.status_code == 402:
                print("   ✅ Payment required (HTTP 402) - as expected")
                payment_data = response.json()
                print(f"   💰 Required payment: {payment_data.get('paymentRequirements', [{}])[0].get('amount', 'N/A')} USDC")
            else:
                print(f"   ⚠️  Unexpected response without payment: {response.status_code}")

            # Now try with payment
            payment_header = self.simulate_realistic_payment("0.01")
            headers = {"X-PAYMENT": json.dumps(payment_header)}

            response = requests.get(f"{self.base_url}/api/flights/search",
                                  params={"origin": "JFK", "destination": "CDG", "date": "2024-08-01"},
                                  headers=headers)

            print(f"   📊 With payment: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Flight search successful with payment")
                # Parse flight results if needed
                try:
                    data = response.json()
                    print(f"   ✈️  Found flights: {len(data.get('flights', []))}")
                except:
                    print("   📄 Raw response received")
            elif response.status_code == 402:
                print("   ⚠️  Payment verification failed (expected with mock transaction)")
            else:
                print(f"   ⚠️  Unexpected response: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception in flight search: {e}")

    def book_flight_with_payment(self):
        """Step 3: Book flight with payment (0.10 USDC)"""
        print("\n✈️ Step 3: Booking flight (0.10 USDC payment)...")

        try:
            payment_header = self.simulate_realistic_payment("0.10")
            booking_data = {
                "flight_id": "AF123-CDG-20240801",
                "passenger_name": "John Traveler",
                "passenger_email": "john@example.com",
                "payment_method": "crypto",
                "plan_id": self.plan_id
            }

            headers = {
                "Content-Type": "application/json",
                "X-PAYMENT": json.dumps(payment_header)
            }

            response = requests.post(f"{self.base_url}/api/flights/book",
                                   json=booking_data, headers=headers)

            if response.status_code == 200:
                data = response.json()
                self.booking_id = data.get("booking_id")
                print(f"   ✅ Booking successful: {self.booking_id}")
                print(f"   💰 Payment: {data.get('payment_amount')} {data.get('payment_currency')}")
                print(f"   📧 Next step: {data.get('next_step', 'N/A')}")
            elif response.status_code == 402:
                print("   ⚠️  Payment verification failed (expected with mock transaction)")
                payment_data = response.json()
                print(f"   💰 Required payment: {payment_data.get('paymentRequirements', [{}])[0].get('amount', 'N/A')} USDC")
            else:
                print(f"   ⚠️  Booking failed: {response.status_code}")
                print(f"   📄 Response: {response.text[:300]}")
                
        except Exception as e:
            print(f"   ❌ Exception in flight booking: {e}")

    def check_booking_status(self):
        """Step 4: Check booking status"""
        print(f"\n📊 Step 4: Checking booking status for {self.booking_id}...")
        
        try:
            response = requests.get(f"{self.base_url}/api/bookings/{self.booking_id}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Booking found")
                print(f"   📋 Status: {data.get('status', 'N/A')}")
                print(f"   💳 Payment Status: {data.get('payment_status', 'N/A')}")
                print(f"   ✈️  Flight: {data.get('flight_id', 'N/A')}")
            else:
                print(f"   ⚠️  Booking status check failed: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception in booking status check: {e}")

    def calculate_total_costs(self):
        """Step 5: Calculate total costs including x402 fees"""
        print("\n💰 Step 5: Calculating total costs with x402 fees...")
        
        try:
            cost_data = {
                "flights": "Air France - $500",
                "hotels": "Hotel Ritz Paris - $200",
                "activities": "Eiffel Tower Tour - $50"
            }

            response = requests.post(f"{self.base_url}/api/travel/cost-calculation",
                                   json=cost_data,
                                   headers={"Content-Type": "application/json"})

            if response.status_code == 200:
                data = response.json()
                breakdown = data.get('breakdown', {})
                print(f"   ✅ Cost calculation successful")
                print(f"   ✈️  Flights: ${breakdown.get('flights', 0):.2f}")
                print(f"   🏨 Hotels: ${breakdown.get('hotels', 0):.2f}")
                print(f"   🎯 Activities: ${breakdown.get('activities', 0):.2f}")
                print(f"   💸 x402 Fees: ${breakdown.get('total_fees', 0):.3f} USDC")
                print(f"   💰 Grand Total: ${breakdown.get('grand_total', 0):.2f}")
                print(f"   📝 Summary: {data.get('summary', 'N/A')}")
            else:
                print(f"   ❌ Cost calculation failed: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception in cost calculation: {e}")

    def verify_database_records(self):
        """Step 6: Verify database records"""
        print("\n🗄️ Step 6: Verifying database records...")
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="travel_planner",
                user="travel_user",
                password="travel_password",
                port=5432
            )
            cur = conn.cursor()

            # Check plans table
            cur.execute("SELECT COUNT(*) FROM plans")
            plan_count = cur.fetchone()[0]
            print(f"   📊 Total plans in database: {plan_count}")

            if self.plan_id:
                cur.execute("SELECT * FROM plans WHERE id = %s", (self.plan_id,))
                plan = cur.fetchone()
                if plan:
                    print(f"   ✅ Plan {self.plan_id} found in database")
                    print(f"   📍 Destination: {plan[2] if len(plan) > 2 else 'N/A'}")
                else:
                    print(f"   ❌ Plan {self.plan_id} NOT found in database")

            # Check bookings table
            cur.execute("SELECT COUNT(*) FROM bookings")
            booking_count = cur.fetchone()[0]
            print(f"   📊 Total bookings in database: {booking_count}")

            if self.booking_id:
                cur.execute("SELECT * FROM bookings WHERE booking_id = %s", (self.booking_id,))
                booking = cur.fetchone()
                if booking:
                    print(f"   ✅ Booking {self.booking_id} found in database")
                    print(f"   ✈️  Flight ID: {booking[3] if len(booking) > 3 else 'N/A'}")
                    print(f"   👤 Passenger: {booking[4] if len(booking) > 4 else 'N/A'}")
                else:
                    print(f"   ❌ Booking {self.booking_id} NOT found in database")

            conn.close()
            
        except Exception as e:
            print(f"   ⚠️  Database check failed: {e}")
            print("   💡 Make sure PostgreSQL is running and accessible")

    def test_payment_pricing(self):
        """Test payment pricing endpoint"""
        print("\n💳 Testing payment pricing...")
        
        try:
            response = requests.get(f"{self.base_url}/api/payments/pricing")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Payment pricing retrieved")
                print(f"   💰 Pricing: {data.get('pricing', {})}")
                print(f"   🏦 Wallet: {data.get('wallet_address', 'N/A')}")
                print(f"   🌐 Network: {data.get('network', 'N/A')}")
            else:
                print(f"   ❌ Payment pricing failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception in payment pricing: {e}")

def main():
    """Run the complete user journey test"""
    print("🧪 TRAVEL PLANNER USER JOURNEY TEST")
    print("=" * 50)
    
    test = UserJourneyTest()
    
    # Test payment pricing first
    test.test_payment_pricing()
    
    # Run complete journey
    test.run_complete_journey()
    
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY:")
    print(f"   📋 Plan ID: {test.plan_id or 'Not created'}")
    print(f"   ✈️  Booking ID: {test.booking_id or 'Not created'}")
    print(f"   👛 User Wallet: {test.user_wallet}")
    print("   💡 Note: Payment verification fails with mock transactions (expected)")

if __name__ == "__main__":
    main() 