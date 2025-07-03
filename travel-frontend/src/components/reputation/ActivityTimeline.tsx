'use client';

interface ActivityTimelineProps {
  recentRecords: any[];
  totalRecords: number;
}

const getEventIcon = (eventType: string) => {
  switch (eventType) {
    case 'BOOKING_CREATED':
      return (
        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </div>
      );
    case 'BOOKING_PAID':
      return (
        <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      );
    case 'BOOKING_COMPLETED':
      return (
        <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      );
    case 'BOOKING_CANCELLED':
      return (
        <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
      );
    case 'DISPUTE_OPENED':
      return (
        <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
      );
    case 'REFERRAL_BONUS':
      return (
        <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
        </div>
      );
    default:
      return (
        <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      );
  }
};

const getEventColor = (eventType: string) => {
  switch (eventType) {
    case 'BOOKING_CREATED':
      return 'border-blue-200 bg-blue-50';
    case 'BOOKING_PAID':
      return 'border-green-200 bg-green-50';
    case 'BOOKING_COMPLETED':
      return 'border-purple-200 bg-purple-50';
    case 'BOOKING_CANCELLED':
      return 'border-red-200 bg-red-50';
    case 'DISPUTE_OPENED':
      return 'border-orange-200 bg-orange-50';
    case 'REFERRAL_BONUS':
      return 'border-yellow-200 bg-yellow-50';
    default:
      return 'border-gray-200 bg-gray-50';
  }
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 1) {
    return 'Today';
  } else if (diffDays === 2) {
    return 'Yesterday';
  } else if (diffDays <= 7) {
    return `${diffDays - 1} days ago`;
  } else {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }
};

const formatAmount = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export default function ActivityTimeline({ recentRecords, totalRecords }: ActivityTimelineProps) {
  if (!recentRecords || recentRecords.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Activity Yet</h3>
          <p className="text-gray-600">Start booking trips to build your reputation!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
        <div className="text-sm text-gray-600">
          {recentRecords.length} of {totalRecords} records
        </div>
      </div>

      <div className="space-y-6">
        {recentRecords.map((record, index) => (
          <div key={index} className="relative">
            {/* Timeline Line */}
            {index < recentRecords.length - 1 && (
              <div className="absolute left-4 top-8 w-0.5 h-16 bg-gray-200"></div>
            )}

            <div className="flex items-start space-x-4">
              {/* Event Icon */}
              <div className="flex-shrink-0">
                {getEventIcon(record.event_type)}
              </div>

              {/* Event Content */}
              <div className={`flex-1 border rounded-lg p-4 ${getEventColor(record.event_type)}`}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">
                    {record.event_type.replace(/_/g, ' ')}
                  </h3>
                  <span className="text-sm text-gray-500">
                    {formatDate(record.timestamp)}
                  </span>
                </div>

                {/* Trip Details */}
                {record.trip_details && (
                  <div className="mb-3">
                    <div className="flex items-center space-x-2 text-sm text-gray-700">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      <span className="font-medium">
                        {record.trip_details.destination || 'Unknown Destination'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-xs text-gray-600 mt-1">
                      <span>
                        {record.trip_details.start_date} - {record.trip_details.end_date}
                      </span>
                      {record.trip_details.amount && (
                        <span className="font-medium">
                          {formatAmount(record.trip_details.amount)}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Event Description */}
                <p className="text-sm text-gray-600 mb-2">
                  {record.description || `Event: ${record.event_type}`}
                </p>

                {/* Metadata */}
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center space-x-4">
                    {record.reputation_points && (
                      <span className="flex items-center">
                        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                        </svg>
                        {record.reputation_points > 0 ? '+' : ''}{record.reputation_points} points
                      </span>
                    )}
                    {record.booking_id && (
                      <span className="font-mono">
                        #{record.booking_id.slice(-8)}
                      </span>
                    )}
                  </div>
                  {record.ipfs_hash && (
                    <span className="font-mono text-xs">
                      IPFS: {record.ipfs_hash.slice(0, 8)}...
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* View All Button */}
      {totalRecords > recentRecords.length && (
        <div className="mt-6 pt-6 border-t border-gray-200 text-center">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            View All {totalRecords} Records
            <svg className="ml-2 -mr-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
} 