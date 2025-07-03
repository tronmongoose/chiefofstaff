'use client';

interface LeaderboardProps {
  leaderboardData: any;
  currentWallet: string;
}

const getLevelColor = (level: string) => {
  switch (level?.toLowerCase()) {
    case 'new':
      return 'bg-gray-500';
    case 'bronze':
      return 'bg-amber-600';
    case 'silver':
      return 'bg-gray-400';
    case 'gold':
      return 'bg-yellow-500';
    case 'platinum':
      return 'bg-blue-500';
    case 'diamond':
      return 'bg-purple-500';
    default:
      return 'bg-gray-500';
  }
};

const getLevelName = (level: string) => {
  switch (level?.toLowerCase()) {
    case 'new':
      return 'New';
    case 'bronze':
      return 'Bronze';
    case 'silver':
      return 'Silver';
    case 'gold':
      return 'Gold';
    case 'platinum':
      return 'Platinum';
    case 'diamond':
      return 'Diamond';
    default:
      return 'New';
  }
};

export default function Leaderboard({ leaderboardData, currentWallet }: LeaderboardProps) {
  if (!leaderboardData) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const leaderboard = leaderboardData.leaderboard || [];
  const currentUserRank = leaderboard.findIndex(
    (entry: any) => entry.wallet_address === currentWallet
  ) + 1;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Leaderboard</h2>
        <div className="text-sm text-gray-600">
          {leaderboardData.total_participants || leaderboard.length} participants
        </div>
      </div>

      {/* Current User Position */}
      {currentUserRank > 0 && (
        <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-900">Your Position</p>
              <p className="text-xs text-gray-600">Among all travelers</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">#{currentUserRank}</div>
              <div className="text-xs text-gray-600">
                Top {Math.round((currentUserRank / (leaderboardData.total_participants || leaderboard.length)) * 100)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard List */}
      <div className="space-y-3">
        {leaderboard.slice(0, 10).map((entry: any, index: number) => {
          const isCurrentUser = entry.wallet_address === currentWallet;
          const rank = index + 1;
          
          return (
            <div
              key={entry.wallet_address}
              className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 ${
                isCurrentUser 
                  ? 'bg-blue-50 border-2 border-blue-200' 
                  : 'bg-gray-50 hover:bg-gray-100'
              }`}
            >
              {/* Rank */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                rank === 1 ? 'bg-yellow-500 text-white' :
                rank === 2 ? 'bg-gray-400 text-white' :
                rank === 3 ? 'bg-amber-600 text-white' :
                'bg-gray-200 text-gray-700'
              }`}>
                {rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : rank}
              </div>

              {/* User Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <p className={`text-sm font-medium truncate ${
                    isCurrentUser ? 'text-blue-900' : 'text-gray-900'
                  }`}>
                    {entry.wallet_address.slice(0, 6)}...{entry.wallet_address.slice(-4)}
                  </p>
                  {isCurrentUser && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                      You
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-2 mt-1">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium text-white ${getLevelColor(entry.reputation_level)}`}>
                    {getLevelName(entry.reputation_level)}
                  </span>
                  <span className="text-xs text-gray-500">
                    {entry.total_bookings} bookings
                  </span>
                </div>
              </div>

              {/* Score */}
              <div className="text-right">
                <div className={`text-lg font-bold ${
                  isCurrentUser ? 'text-blue-900' : 'text-gray-900'
                }`}>
                  {entry.reputation_score}
                </div>
                <div className="text-xs text-gray-500">
                  {entry.average_rating?.toFixed(1) || 'N/A'} ⭐
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Show More Button */}
      {leaderboard.length > 10 && (
        <div className="mt-6 pt-6 border-t border-gray-200 text-center">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            View Full Leaderboard
            <svg className="ml-2 -mr-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}

      {/* Leaderboard Stats */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Leaderboard Stats</h3>
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <div className="text-lg font-bold text-gray-900">
              {leaderboard[0]?.reputation_score || 0}
            </div>
            <div className="text-xs text-gray-600">Top Score</div>
          </div>
          <div>
            <div className="text-lg font-bold text-gray-900">
              {leaderboard.length > 0 ? Math.round(leaderboard.reduce((sum: number, entry: any) => sum + entry.reputation_score, 0) / leaderboard.length) : 0}
            </div>
            <div className="text-xs text-gray-600">Avg Score</div>
          </div>
        </div>
      </div>

      {/* Top Performers */}
      {leaderboard.length >= 3 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Top Performers</h3>
          <div className="space-y-2">
            {leaderboard.slice(0, 3).map((entry: any, index: number) => (
              <div key={entry.wallet_address} className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <span className="text-gray-500">#{index + 1}</span>
                  <span className="font-medium text-gray-900">
                    {entry.wallet_address.slice(0, 4)}...{entry.wallet_address.slice(-4)}
                  </span>
                </div>
                <div className="text-gray-600">
                  {entry.reputation_score} pts
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 