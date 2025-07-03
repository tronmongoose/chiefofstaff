'use client';

interface AchievementBadgesProps {
  reputationData: any;
}

const achievements = [
  {
    id: 'first_booking',
    name: 'First Steps',
    description: 'Complete your first booking',
    icon: '🎯',
    color: 'from-blue-400 to-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    condition: (data: any) => data?.total_bookings >= 1,
    progress: (data: any) => Math.min(data?.total_bookings || 0, 1),
    maxProgress: 1
  },
  {
    id: 'trusted_traveler',
    name: 'Trusted Traveler',
    description: 'Complete 5 bookings with 4.5+ rating',
    icon: '⭐',
    color: 'from-yellow-400 to-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    condition: (data: any) => data?.total_bookings >= 5 && data?.average_rating >= 4.5,
    progress: (data: any) => Math.min(data?.total_bookings || 0, 5),
    maxProgress: 5
  },
  {
    id: 'explorer',
    name: 'Explorer',
    description: 'Visit 3 different countries',
    icon: '🌍',
    color: 'from-green-400 to-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    condition: (data: any) => (data?.countries_visited?.length || 0) >= 3,
    progress: (data: any) => Math.min(data?.countries_visited?.length || 0, 3),
    maxProgress: 3
  },
  {
    id: 'high_roller',
    name: 'High Roller',
    description: 'Spend $10,000+ on travel',
    icon: '💰',
    color: 'from-purple-400 to-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    condition: (data: any) => data?.total_spent_usd >= 10000,
    progress: (data: any) => Math.min(data?.total_spent_usd || 0, 10000),
    maxProgress: 10000
  },
  {
    id: 'perfect_record',
    name: 'Perfect Record',
    description: '100% completion rate with 10+ bookings',
    icon: '🏆',
    color: 'from-red-400 to-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    condition: (data: any) => data?.total_bookings >= 10 && data?.completion_rate === 1,
    progress: (data: any) => Math.min(data?.total_bookings || 0, 10),
    maxProgress: 10
  },
  {
    id: 'referral_master',
    name: 'Referral Master',
    description: 'Successfully refer 5 travelers',
    icon: '🤝',
    color: 'from-indigo-400 to-indigo-600',
    bgColor: 'bg-indigo-50',
    borderColor: 'border-indigo-200',
    condition: (data: any) => data?.successful_referrals >= 5,
    progress: (data: any) => Math.min(data?.successful_referrals || 0, 5),
    maxProgress: 5
  },
  {
    id: 'seasoned_traveler',
    name: 'Seasoned Traveler',
    description: 'Complete 25 bookings',
    icon: '✈️',
    color: 'from-teal-400 to-teal-600',
    bgColor: 'bg-teal-50',
    borderColor: 'border-teal-200',
    condition: (data: any) => data?.total_bookings >= 25,
    progress: (data: any) => Math.min(data?.total_bookings || 0, 25),
    maxProgress: 25
  },
  {
    id: 'dispute_free',
    name: 'Dispute Free',
    description: '50+ bookings with 0 disputes',
    icon: '🛡️',
    color: 'from-emerald-400 to-emerald-600',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    condition: (data: any) => data?.total_bookings >= 50 && data?.disputed_bookings === 0,
    progress: (data: any) => Math.min(data?.total_bookings || 0, 50),
    maxProgress: 50
  }
];

export default function AchievementBadges({ reputationData }: AchievementBadgesProps) {
  if (!reputationData) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const stats = reputationData.reputation_summary;
  const unlockedAchievements = achievements.filter(achievement => 
    achievement.condition(stats)
  );
  const lockedAchievements = achievements.filter(achievement => 
    !achievement.condition(stats)
  );

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Achievement Badges</h2>
        <div className="text-sm text-gray-600">
          {unlockedAchievements.length} of {achievements.length} unlocked
        </div>
      </div>

      {/* Progress Overview */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm text-gray-600">
            {Math.round((unlockedAchievements.length / achievements.length) * 100)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${(unlockedAchievements.length / achievements.length) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Unlocked Achievements */}
      {unlockedAchievements.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Unlocked</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {unlockedAchievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`relative p-4 rounded-lg border-2 ${achievement.borderColor} ${achievement.bgColor} text-center group hover:shadow-md transition-all duration-200`}
              >
                <div className="text-3xl mb-2">{achievement.icon}</div>
                <h4 className="font-semibold text-gray-900 text-sm mb-1">
                  {achievement.name}
                </h4>
                <p className="text-xs text-gray-600 mb-3">
                  {achievement.description}
                </p>
                <div className="absolute top-2 right-2">
                  <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="text-xs text-gray-500">
                  {achievement.progress(stats)}/{achievement.maxProgress}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Locked Achievements */}
      {lockedAchievements.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Locked</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {lockedAchievements.map((achievement) => (
              <div
                key={achievement.id}
                className="relative p-4 rounded-lg border-2 border-gray-200 bg-gray-50 text-center group hover:shadow-md transition-all duration-200 opacity-60"
              >
                <div className="text-3xl mb-2 filter grayscale">{achievement.icon}</div>
                <h4 className="font-semibold text-gray-700 text-sm mb-1">
                  {achievement.name}
                </h4>
                <p className="text-xs text-gray-500 mb-3">
                  {achievement.description}
                </p>
                <div className="absolute top-2 right-2">
                  <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="text-xs text-gray-400">
                  {achievement.progress(stats)}/{achievement.maxProgress}
                </div>
                
                {/* Progress Bar for Locked Achievements */}
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-1">
                    <div 
                      className="bg-gray-400 h-1 rounded-full transition-all duration-500"
                      style={{ width: `${(achievement.progress(stats) / achievement.maxProgress) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Achievement Stats */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">{unlockedAchievements.length}</div>
            <div className="text-sm text-gray-600">Unlocked</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{lockedAchievements.length}</div>
            <div className="text-sm text-gray-600">Locked</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_bookings}</div>
            <div className="text-sm text-gray-600">Total Bookings</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{stats.countries_visited?.length || 0}</div>
            <div className="text-sm text-gray-600">Countries</div>
          </div>
        </div>
      </div>
    </div>
  );
} 