# Travel Planner Frontend

A modern Next.js frontend for the AI-powered travel planning system with LangGraph backend.

## Features

- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Real-time Plan Generation**: AI-powered travel planning with detailed itineraries
- **Plan Review & Confirmation**: Interactive plan review with booking confirmation
- **User Dashboard**: View and manage past travel plans
- **Global State Management**: React Context for seamless state sharing
- **Error Handling**: Graceful error handling with user-friendly alerts
- **Loading States**: Smooth loading indicators throughout the app

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **TypeScript**: Full type safety
- **Responsive Design**: Mobile-first approach

## Getting Started

### Prerequisites

- Node.js 18+ 
- Backend server running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Page Flow & Testing

### 1. Home Page (`/`)
- **Purpose**: Generate new travel plans
- **Testing Steps**:
  1. Enter destination (e.g., "Paris", "Tokyo", "New York")
  2. Enter budget in USD (e.g., 2000)
  3. Enter wallet address (e.g., "0x1234567890123456789012345678901234567890")
  4. Click "Generate Plan"
  5. Verify loading state and automatic navigation to Review page

### 2. Review Page (`/review`)
- **Purpose**: Review and confirm generated travel plans
- **Testing Steps**:
  1. Verify plan details are displayed correctly
  2. Check flights, hotels, activities, and cost breakdown
  3. Click "Confirm & Book Trip"
  4. Verify confirmation process and navigation to Dashboard
  5. Test "Back to Home" button

### 3. Dashboard Page (`/dashboard`)
- **Purpose**: View and manage past travel plans
- **Testing Steps**:
  1. Verify confirmed plans are displayed
  2. Check plan cards show destination, cost, status, and creation date
  3. Click "View Details" on a plan to reload it in Review page
  4. Test "Create New Plan" button navigation
  5. Verify empty state when no plans exist

## API Integration

The frontend integrates with the following backend endpoints:

- `POST /generate_plan` - Generate new travel plans
- `POST /confirm_plan` - Confirm and book travel plans
- `GET /get_user_plans/{wallet}` - Retrieve user's travel plans

## State Management

The app uses React Context (`PlanContext`) to manage:
- Current travel plan
- User wallet address
- Loading states
- Error messages
- Plan generation and confirmation methods

State is persisted in localStorage for seamless navigation.

## Error Handling

- Network errors are displayed as dismissible alerts
- Form validation prevents invalid submissions
- Loading states prevent multiple submissions
- Graceful fallbacks for missing data

## UI Components

- **GlobalHeader**: Navigation with hover effects
- **GlobalLoadingBar**: Top loading indicator
- **GlobalErrorAlert**: Dismissible error notifications
- **Responsive Cards**: Plan display with hover effects
- **Modern Forms**: Input fields with focus states
- **Gradient Buttons**: Interactive buttons with animations

## Development

### File Structure
```
src/
├── app/
│   ├── page.tsx              # Home page
│   ├── review/
│   │   └── page.tsx          # Review page
│   ├── dashboard/
│   │   └── page.tsx          # Dashboard page
│   └── layout.tsx            # Root layout
├── components/
│   ├── GlobalHeader.tsx      # Navigation header
│   ├── GlobalLoadingBar.tsx  # Loading indicator
│   └── GlobalErrorAlert.tsx  # Error notifications
└── context/
    └── PlanContext.tsx       # State management
```

### Key Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: Proper ARIA labels and keyboard navigation
- **Performance**: Optimized with Next.js App Router
- **Type Safety**: Full TypeScript implementation

## Testing the Full Flow

1. **Start Backend**: `./start_backend.sh` (from project root)
2. **Start Frontend**: `npm run dev` (from travel-frontend directory)
3. **Test Complete Flow**:
   - Generate a plan on Home page
   - Review and confirm on Review page
   - View confirmed plan in Dashboard
   - Select past plan to reload details

## Troubleshooting

- **CORS Issues**: Ensure backend has CORS enabled for localhost:3000
- **API Errors**: Check backend logs for detailed error messages
- **State Issues**: Clear localStorage if state becomes inconsistent
- **Loading Issues**: Verify backend is running on port 8000

## Future Enhancements

- User authentication and profiles
- Plan sharing and social features
- Advanced filtering and search
- Real-time notifications
- Payment integration
- Plan templates and favorites
