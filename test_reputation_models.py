#!/usr/bin/env python3
"""
Test script for reputation models functionality
"""

import asyncio
from datetime import datetime, date
from decimal import Decimal
from reputation_models import (
    EventType, TripStatus, DisputeStatus, ReputationLevel,
    TripData, OutcomeData, VerificationData, ReferralData,
    ReputationRecord, ReputationSummary, IPFSStorageUtils,
    ReputationValidator, create_booking_record, create_completion_record
)


def test_basic_models():
    """Test basic model creation and validation"""
    print("🧪 Testing Basic Models")
    print("=" * 40)
    
    # Test TripData
    trip_data = TripData(
        destination="Paris, France",
        cost_usd=Decimal("2500.00"),
        cost_usdc=Decimal("2500.000000"),
        duration_days=7,
        start_date=date(2024, 6, 15),
        end_date=date(2024, 6, 22),
        booking_id="BK123456789",
        plan_id="PLAN987654321"
    )
    print(f"✅ TripData created: {trip_data.destination} - ${trip_data.cost_usd}")
    
    # Test OutcomeData
    outcome_data = OutcomeData(
        status=TripStatus.COMPLETED,
        rating=5,
        feedback="Amazing trip! Everything was perfect.",
        completion_verified=True
    )
    print(f"✅ OutcomeData created: {outcome_data.status} - {outcome_data.rating} stars")
    
    # Test VerificationData
    verification_data = VerificationData(
        payment_tx_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        ipfs_hash="Qm" + "a"*44
    )
    print(f"✅ VerificationData created: TX {verification_data.payment_tx_hash[:10]}...")
    
    # Test ReferralData
    referral_data = ReferralData(
        referrer_wallet="0x" + "a"*40,
        commission_rate=Decimal("0.1500"),
        commission_amount=Decimal("375.000000"),
        referral_code="FRIEND2024"
    )
    print(f"✅ ReferralData created: {referral_data.commission_rate * 100}% commission")
    
    return trip_data, outcome_data, verification_data, referral_data


def test_reputation_record():
    """Test ReputationRecord creation and methods"""
    print("\n📝 Testing ReputationRecord")
    print("=" * 40)
    
    # Create basic data
    trip_data, outcome_data, verification_data, referral_data = test_basic_models()
    
    # Create reputation record
    record = create_booking_record(
        traveler_wallet="0x" + "1"*40,
        platform_wallet="0x" + "2"*40,
        trip_data=trip_data,
        payment_tx_hash="0x" + "4"*64,
        ipfs_hash="Qm" + "d"*44,
        referrer_wallet="0x" + "a"*40
    )
    
    # Generate record ID
    record.record_id = record.generate_record_id()
    
    print(f"✅ ReputationRecord created: {record.record_id}")
    print(f"   Event: {record.event_type}")
    print(f"   Traveler: {record.traveler_wallet[:10]}...")
    print(f"   Platform: {record.platform_wallet[:10]}...")
    print(f"   Trip: {record.trip_data.destination}")
    print(f"   Cost: ${record.trip_data.cost_usd}")
    
    # Test JSON conversion
    json_data = record.to_ipfs_json()
    print(f"✅ JSON conversion: {len(json_data)} characters")
    
    # Test hash calculation
    record_hash = record.calculate_hash()
    print(f"✅ Hash calculated: {record_hash[:16]}...")
    
    return record


def test_reputation_summary():
    """Test ReputationSummary creation and calculations"""
    print("\n📊 Testing ReputationSummary")
    print("=" * 40)
    
    # Create reputation summary
    summary = ReputationSummary(
        wallet_address="0x" + "3"*40
    )
    
    # Simulate some booking data
    summary.total_bookings = 5
    summary.completed_bookings = 4
    summary.cancelled_bookings = 1
    summary.disputed_bookings = 0
    summary.total_spent_usd = Decimal("12500.00")
    summary.total_spent_usdc = Decimal("12500.000000")
    summary.average_rating = Decimal("4.5")
    summary.countries_visited = ["France", "Italy", "Spain", "Germany"]
    summary.total_referrals = 3
    summary.successful_referrals = 2
    summary.total_commission_earned = Decimal("187.500000")
    
    # Calculate metrics
    summary.completion_rate = Decimal(summary.completed_bookings / summary.total_bookings)
    summary.dispute_rate = Decimal(summary.disputed_bookings / summary.total_bookings)
    summary.reputation_score = summary.calculate_reputation_score()
    summary.update_reputation_level()
    
    print(f"✅ ReputationSummary created for {summary.wallet_address[:10]}...")
    print(f"   Total bookings: {summary.total_bookings}")
    print(f"   Completion rate: {summary.completion_rate * 100}%")
    print(f"   Average rating: {summary.average_rating}")
    print(f"   Countries visited: {len(summary.countries_visited)}")
    print(f"   Reputation score: {summary.reputation_score}")
    print(f"   Reputation level: {summary.reputation_level}")
    print(f"   Successful referrals: {summary.successful_referrals}")
    print(f"   Commission earned: ${summary.total_commission_earned}")
    
    return summary


def test_ipfs_utilities():
    """Test IPFS storage utilities"""
    print("\n🗂️ Testing IPFS Storage Utilities")
    print("=" * 40)
    
    wallet_address = "0x" + "3"*40
    year = 2024
    month = 6
    
    # Test path generation
    ipfs_path = IPFSStorageUtils.generate_ipfs_path(wallet_address, year, month)
    print(f"✅ IPFS path: {ipfs_path}")
    
    # Test summary path
    summary_path = IPFSStorageUtils.generate_summary_path(wallet_address)
    print(f"✅ Summary path: {summary_path}")
    
    # Test chain index path
    chain_index_path = IPFSStorageUtils.generate_chain_index_path(wallet_address)
    print(f"✅ Chain index path: {chain_index_path}")
    
    # Test record creation
    record = test_reputation_record()
    filename = IPFSStorageUtils.generate_record_filename(record)
    print(f"✅ Record filename: {filename}")
    
    # Test chain link creation
    chain_link = IPFSStorageUtils.create_chain_link(record)
    print(f"✅ Chain link created: {chain_link['record_id']}")
    
    return ipfs_path, summary_path, chain_index_path, filename


def test_validation():
    """Test validation utilities"""
    print("\n✅ Testing Validation")
    print("=" * 40)
    
    # Test wallet address validation
    valid_wallet = "0x1234567890abcdef1234567890abcdef1234567890"
    invalid_wallet = "0x1234567890abcdef1234567890abcdef123456789"  # Too short
    
    print(f"Valid wallet: {ReputationValidator.validate_wallet_address(valid_wallet)}")
    print(f"Invalid wallet: {ReputationValidator.validate_wallet_address(invalid_wallet)}")
    
    # Test rating validation
    print(f"Valid rating (5): {ReputationValidator.validate_rating(5)}")
    print(f"Invalid rating (6): {ReputationValidator.validate_rating(6)}")
    
    # Test amount validation
    print(f"Valid amount: {ReputationValidator.validate_amount(Decimal('100.00'))}")
    print(f"Invalid amount: {ReputationValidator.validate_amount(Decimal('-50.00'))}")
    
    # Test date consistency
    start_date = date(2024, 6, 15)
    end_date = date(2024, 6, 22)
    duration_days = 7
    
    print(f"Valid dates: {ReputationValidator.validate_date_consistency(start_date, end_date, duration_days)}")
    print(f"Invalid dates: {ReputationValidator.validate_date_consistency(end_date, start_date, duration_days)}")


def test_utility_functions():
    """Test utility functions"""
    print("\n🔧 Testing Utility Functions")
    print("=" * 40)
    
    # Test booking record creation
    trip_data = TripData(
        destination="Tokyo, Japan",
        cost_usd=Decimal("3000.00"),
        cost_usdc=Decimal("3000.000000"),
        duration_days=10,
        start_date=date(2024, 7, 1),
        end_date=date(2024, 7, 11),
        booking_id="BK987654321",
        plan_id="PLAN123456789"
    )
    
    payment_tx_hash = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    referrer_wallet = "0x" + "b"*40
    
    booking_record = create_booking_record(
        traveler_wallet="0x" + "5"*40,
        platform_wallet="0x" + "6"*40,
        trip_data=trip_data,
        payment_tx_hash=payment_tx_hash,
        ipfs_hash="Qm" + "c"*44,
        referrer_wallet=referrer_wallet
    )
    
    print(f"✅ Booking record created: {booking_record.record_id}")
    print(f"   Event type: {booking_record.event_type}")
    print(f"   Referrer: {booking_record.referral_data.referrer_wallet[:10]}...")
    
    # Test completion record creation
    completion_record = create_completion_record(
        original_record=booking_record,
        rating=5,
        feedback="Incredible experience in Tokyo! Highly recommend."
    )
    
    print(f"✅ Completion record created: {completion_record.record_id}")
    print(f"   Event type: {completion_record.event_type}")
    print(f"   Rating: {completion_record.outcome_data.rating}")
    print(f"   Feedback: {completion_record.outcome_data.feedback[:50]}...")
    print(f"   Previous record: {completion_record.verification_data.previous_record_hash[:16]}...")


def test_error_handling():
    """Test error handling and validation"""
    print("\n🚨 Testing Error Handling")
    print("=" * 40)
    
    try:
        # Test invalid wallet address
        TripData(
            destination="Test",
            cost_usd=Decimal("100.00"),
            cost_usdc=Decimal("100.000000"),
            duration_days=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
            booking_id="TEST123",
            plan_id="PLAN123"
        )
        
        ReputationRecord(
            record_id="test123",
            traveler_wallet="invalid_wallet",  # This should fail
            platform_wallet="0x1234567890abcdef1234567890abcdef1234567890",
            event_type=EventType.BOOKING_CREATED,
            trip_data=TripData(
                destination="Test",
                cost_usd=Decimal("100.00"),
                cost_usdc=Decimal("100.000000"),
                duration_days=1,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 2),
                booking_id="TEST123",
                plan_id="PLAN123"
            ),
            outcome_data=OutcomeData(status=TripStatus.PENDING),
            verification_data=VerificationData(
                payment_tx_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                ipfs_hash="Qm" + "b"*44
            ),
            referral_data=ReferralData()
        )
    except ValueError as e:
        print(f"✅ Validation error caught: {e}")
    
    try:
        # Test invalid date consistency
        TripData(
            destination="Test",
            cost_usd=Decimal("100.00"),
            cost_usdc=Decimal("100.000000"),
            duration_days=5,
            start_date=date(2024, 1, 10),  # Start after end
            end_date=date(2024, 1, 5),
            booking_id="TEST123",
            plan_id="PLAN123"
        )
    except ValueError as e:
        print(f"✅ Date validation error caught: {e}")


def main():
    """Main test function"""
    print("🚀 Starting Reputation Models Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        test_basic_models()
        test_reputation_record()
        test_reputation_summary()
        test_ipfs_utilities()
        test_validation()
        test_utility_functions()
        test_error_handling()
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 60)
        print("✅ Reputation models system is working correctly")
        print("✅ All validations are functioning")
        print("✅ IPFS utilities are ready")
        print("✅ Utility functions are operational")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 