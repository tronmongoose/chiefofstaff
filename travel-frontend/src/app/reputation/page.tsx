'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useWallet } from '@/context/WalletContext';
import ReputationScore from '@/components/reputation/ReputationScore';
import TravelStats from '@/components/reputation/TravelStats';
import ActivityTimeline from '@/components/reputation/ActivityTimeline';
import AchievementBadges from '@/components/reputation/AchievementBadges';
import ReferralStats from '@/components/reputation/ReferralStats';
import Leaderboard from '@/components/reputation/Leaderboard';
import LoadingSpinner from '@/components/LoadingSpinner';

interface ReputationData {
  wallet_address: string;
  reputation_summary: {
    reputation_level: string;
    reputation_score: number;
    total_bookings: number;
    completed_bookings: number;
    cancelled_bookings: number;
    disputed_bookings: number;
    total_spent_usd: number;
    average_rating: number;
    completion_rate: number;
    dispute_rate: number;
    countries_visited: string[];
    total_travel_days: number;
    total_referrals: number;
    successful_referrals: number;
    total_commission_earned: number;
    total_bonus_earned: number;
    first_booking_date: string;
    last_booking_date: string;
  };
  recent_records: any[];
  total_records: number;
}

interface LeaderboardData {
  leaderboard: Array<{
    wallet_address: string;
    reputation_score: number;
    reputation_level: string;
    total_bookings: number;
    completed_bookings: number;
    average_rating: number;
    countries_visited: number;
  }>;
  total_participants: number;
}

interface LevelsData {
  levels_info: {
    levels: Array<{
      level: string;
      name: string;
      min_score: number;
      max_score: number;
      benefits: string[];
    }>;
    scoring_factors: Record<string, string>;
  };
}

export default function ReputationDashboard() {
  const searchParams = useSearchParams();
  const { address, isConnected, connect } = useWallet();
  const [walletAddress, setWalletAddress] = useState<string>('');
  const [reputationData, setReputationData] = useState<ReputationData | null>(null);
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardData | null>(null);
  const [levelsData, setLevelsData] = useState<LevelsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Use connected wallet, URL params, or demo wallet as fallback
    const wallet = address || searchParams.get('wallet') || '0x1234567890abcdef1234567890abcdef1234567890';
    setWalletAddress(wallet);
    loadReputationData(wallet);
  }, [searchParams, address]);

  const loadReputationData = async (wallet: string) => {
    setLoading(true);
    setError(null);

    try {
      // Load reputation data
      const reputationResponse = await fetch(`/api/reputation/${wallet}`);
      const reputationResult = await reputationResponse.json();

      // Load leaderboard data
      const leaderboardResponse = await fetch('/api/reputation/leaderboard?limit=10');
      const leaderboardResult = await leaderboardResponse.json();

      // Load levels data
      const levelsResponse = await fetch('/api/reputation/levels');
      const levelsResult = await levelsResponse.json();

      if (reputationResult.status === 'success') {
        setReputationData(reputationResult);
      }

      if (leaderboardResult.status === 'success') {
        setLeaderboardData(leaderboardResult);
      }

      if (levelsResult.status === 'success') {
        setLevelsData(levelsResult);
      }

    } catch (err) {
      setError('Failed to load reputation data');
      console.error('Error loading reputation data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLevel = () => {
    if (!reputationData || !levelsData) return null;
    
    const score = reputationData.reputation_summary.reputation_score;
    return levelsData.levels_info.levels.find(level => 
      score >= level.min_score && score <= level.max_score
    );
  };

  const getNextLevel = () => {
    if (!reputationData || !levelsData) return null;
    
    const score = reputationData.reputation_summary.reputation_score;
    return levelsData.levels_info.levels.find(level => 
      score < level.min_score
    );
  };

  // Show wallet connection prompt if no wallet connected and no URL wallet specified
  if (!isConnected && !searchParams.get('wallet')) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="text-6xl mb-6">🔗</div>
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Connect Your Wallet</h2>
          <p className="text-gray-600 mb-6">
            Connect your Coinbase Wallet to view your travel reputation and achievements.
          </p>
          <button
            onClick={connect}
            className="bg-blue-600 text-white px-8 py-4 rounded-xl hover:bg-blue-700 font-semibold text-lg"
          >
            Connect Wallet
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Error Loading Reputation</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => loadReputationData(walletAddress)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const currentLevel = getCurrentLevel();
  const nextLevel = getNextLevel();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Reputation Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Building trust through transparent travel history
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Wallet Address</p>
              <p className="font-mono text-sm text-gray-700">
                {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Main Reputation Info */}
          <div className="lg:col-span-2 space-y-8">
            {/* Reputation Score Card */}
            <ReputationScore 
              reputationData={reputationData}
              currentLevel={currentLevel}
              nextLevel={nextLevel}
            />

            {/* Travel Statistics */}
            <TravelStats reputationData={reputationData} />

            {/* Recent Activity Timeline */}
            <ActivityTimeline 
              recentRecords={reputationData?.recent_records || []}
              totalRecords={reputationData?.total_records || 0}
            />

            {/* Achievement Badges */}
            <AchievementBadges reputationData={reputationData} />
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-8">
            {/* Referral Statistics */}
            <ReferralStats reputationData={reputationData} />

            {/* Leaderboard */}
            <Leaderboard 
              leaderboardData={leaderboardData}
              currentWallet={walletAddress}
            />
          </div>
        </div>
      </div>
    </div>
  );
} 