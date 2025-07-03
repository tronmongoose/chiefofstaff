'use client';

interface ReputationScoreProps {
  reputationData: any;
  currentLevel: any;
  nextLevel: any;
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

const getLevelGradient = (level: string) => {
  switch (level?.toLowerCase()) {
    case 'new':
      return 'from-gray-400 to-gray-600';
    case 'bronze':
      return 'from-amber-500 to-amber-700';
    case 'silver':
      return 'from-gray-300 to-gray-500';
    case 'gold':
      return 'from-yellow-400 to-yellow-600';
    case 'platinum':
      return 'from-blue-400 to-blue-600';
    case 'diamond':
      return 'from-purple-400 to-purple-600';
    default:
      return 'from-gray-400 to-gray-600';
  }
};

export default function ReputationScore({ reputationData, currentLevel, nextLevel }: ReputationScoreProps) {
  if (!reputationData) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-6"></div>
          <div className="h-6 bg-gray-200 rounded w-full mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  const score = reputationData.reputation_summary.reputation_score;
  const maxScore = 1000;
  const progressPercentage = Math.min((score / maxScore) * 100, 100);

  const pointsToNext = nextLevel ? nextLevel.min_score - score : 0;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Reputation Score</h2>
          <p className="text-gray-600">Your trust level in the travel community</p>
        </div>
        <div className="text-right">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white ${getLevelColor(currentLevel?.level)}`}>
            {currentLevel?.name || 'New Traveler'}
          </div>
        </div>
      </div>

      {/* Score Display */}
      <div className="text-center mb-6">
        <div className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          {score}
        </div>
        <div className="text-gray-500 text-sm">out of {maxScore} points</div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{Math.round(progressPercentage)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full bg-gradient-to-r ${getLevelGradient(currentLevel?.level)} transition-all duration-500`}
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>

      {/* Level Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Current Level</h3>
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 rounded-full ${getLevelColor(currentLevel?.level)} flex items-center justify-center`}>
              <span className="text-white text-sm font-bold">
                {currentLevel?.level?.charAt(0).toUpperCase() || 'N'}
              </span>
            </div>
            <div>
              <div className="font-medium text-gray-900">{currentLevel?.name || 'New Traveler'}</div>
              <div className="text-sm text-gray-600">
                {currentLevel?.min_score || 0} - {currentLevel?.max_score || 24} points
              </div>
            </div>
          </div>
          {currentLevel?.benefits && (
            <div className="mt-3">
              <div className="text-sm text-gray-600 mb-1">Benefits:</div>
              <ul className="text-xs text-gray-500 space-y-1">
                {currentLevel.benefits.slice(0, 2).map((benefit: string, index: number) => (
                  <li key={index} className="flex items-center">
                    <span className="text-green-500 mr-1">✓</span>
                    {benefit}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {nextLevel && (
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Next Level</h3>
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-full ${getLevelColor(nextLevel.level)} flex items-center justify-center opacity-60`}>
                <span className="text-white text-sm font-bold">
                  {nextLevel.level.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <div className="font-medium text-gray-900">{nextLevel.name}</div>
                <div className="text-sm text-gray-600">
                  {pointsToNext} more points needed
                </div>
              </div>
            </div>
            {nextLevel.benefits && (
              <div className="mt-3">
                <div className="text-sm text-gray-600 mb-1">Unlock benefits:</div>
                <ul className="text-xs text-gray-500 space-y-1">
                  {nextLevel.benefits.slice(0, 2).map((benefit: string, index: number) => (
                    <li key={index} className="flex items-center">
                      <span className="text-blue-500 mr-1">🔒</span>
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {reputationData.reputation_summary.total_bookings}
            </div>
            <div className="text-sm text-gray-600">Total Bookings</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {reputationData.reputation_summary.completed_bookings}
            </div>
            <div className="text-sm text-gray-600">Completed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {reputationData.reputation_summary.average_rating?.toFixed(1) || 'N/A'}
            </div>
            <div className="text-sm text-gray-600">Avg Rating</div>
          </div>
        </div>
      </div>
    </div>
  );
} 