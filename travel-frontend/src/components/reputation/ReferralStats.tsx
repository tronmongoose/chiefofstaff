'use client';

interface ReferralStatsProps {
  reputationData: any;
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export default function ReferralStats({ reputationData }: ReferralStatsProps) {
  if (!reputationData) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const stats = reputationData.reputation_summary;
  const referralRate = stats.total_referrals > 0 
    ? (stats.successful_referrals / stats.total_referrals) * 100 
    : 0;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Referral Program</h2>
        <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
      </div>

      {/* Referral Link */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">Your Referral Link</h3>
        <div className="flex items-center space-x-2">
          <input
            type="text"
            readOnly
            value={`https://travelapp.com/ref/${reputationData.wallet_address.slice(0, 8)}`}
            className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button className="px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors">
            Copy
          </button>
        </div>
        <p className="text-xs text-gray-600 mt-2">
          Share this link to earn rewards when friends book their first trip
        </p>
      </div>

      {/* Referral Stats */}
      <div className="space-y-4 mb-6">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Total Referrals</p>
              <p className="text-xs text-gray-600">People you've invited</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-gray-900">{stats.total_referrals}</p>
          </div>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Successful Referrals</p>
              <p className="text-xs text-gray-600">Completed first bookings</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-gray-900">{stats.successful_referrals}</p>
            <p className="text-xs text-gray-600">{referralRate.toFixed(1)}% success rate</p>
          </div>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Commission Earned</p>
              <p className="text-xs text-gray-600">From successful referrals</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-gray-900">{formatCurrency(stats.total_commission_earned)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Bonus Earned</p>
              <p className="text-xs text-gray-600">Achievement bonuses</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-gray-900">{formatCurrency(stats.total_bonus_earned)}</p>
          </div>
        </div>
      </div>

      {/* Total Earnings */}
      <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-gray-900">Total Earnings</p>
            <p className="text-xs text-gray-600">From referral program</p>
          </div>
          <div className="text-right">
            <p className="text-xl font-bold text-green-600">
              {formatCurrency(stats.total_commission_earned + stats.total_bonus_earned)}
            </p>
          </div>
        </div>
      </div>

      {/* Referral Tiers */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Referral Tiers</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">1-5 referrals</span>
            <span className="font-medium text-gray-900">$10 per booking</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">6-15 referrals</span>
            <span className="font-medium text-gray-900">$15 per booking</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">16+ referrals</span>
            <span className="font-medium text-gray-900">$20 per booking</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
          View Referral History
        </button>
      </div>
    </div>
  );
} 