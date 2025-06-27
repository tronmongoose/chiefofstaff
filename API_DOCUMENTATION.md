# 🚀 Travel Planning API Documentation

## Overview

The Travel Planning API provides a complete backend service for generating, managing, and confirming travel plans. The API is fully decoupled from any frontend framework and supports modern web applications.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses wallet addresses for user identification. In production, implement proper JWT authentication.

## CORS Support

The API supports CORS for the following origins:
- `http://localhost:3000` (React/Next.js)
- `http://localhost:5173` (Vite)
- `http://localhost:8080` (Vue)
- `http://localhost:4200` (Angular)
- `http://localhost:8501` (Streamlit)

## API Endpoints

### 1. Generate Travel Plan

**Endpoint:** `POST /generate_plan`

**Description:** Generate a complete travel plan based on destination and budget.

**Request Body:**
```json
{
  "destination": "Paris",
  "budget": 2000.0,
  "user_wallet": "0x1234567890abcdef",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "status": "success",
  "plan": {
    "destination": "Paris",
    "flights": [
      {
        "from_location": "JFK",
        "to_location": "Paris",
        "airline": "DemoAir",
        "dates": "2024-08-01 to 2024-08-10",
        "price": 500.0
      }
    ],
    "hotels": [
      {
        "name": "Hotel Demo",
        "location": "Paris",
        "price_per_night": 150.0,
        "nights": 7,
        "total": 1050.0
      }
    ],
    "activities": [
      "Eiffel Tower visit",
      "Louvre Museum tour",
      "Seine River cruise"
    ],
    "total_cost": 1750.0,
    "platform_fee": 35.0,
    "grand_total": 1785.0,
    "plan_id": "31d7d00c-bf95-4fde-8e1f-4155ae1f6395",
    "created_at": "2025-06-27T09:34:25.205971"
  },
  "formatted_plan": "# 🗺️ Travel Itinerary for Paris...",
  "error": null
}
```

**Error Response:**
```json
{
  "status": "error",
  "plan": null,
  "formatted_plan": null,
  "error": "Plan exceeds budget. Please increase your budget or try a different destination."
}
```

### 2. Confirm Travel Plan

**Endpoint:** `POST /confirm_plan`

**Description:** Confirm a travel plan and process payment/booking.

**Request Body:**
```json
{
  "plan_id": "31d7d00c-bf95-4fde-8e1f-4155ae1f6395",
  "user_wallet": "0x1234567890abcdef",
  "payment_method": "cdp",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "status": "success",
  "booking_status": {
    "flights": "confirmed",
    "hotels": "confirmed",
    "activities": "confirmed"
  },
  "payment_status": "success",
  "confirmation_message": "✅ Travel Plan Confirmed!\n\nYour trip to Paris has been successfully booked...",
  "error": null
}
```

### 3. Get User Plans

**Endpoint:** `GET /get_user_plans/{user_wallet}`

**Description:** Retrieve all plans associated with a user wallet.

**Response:**
```json
{
  "status": "success",
  "plans": [
    {
      "plan_id": "31d7d00c-bf95-4fde-8e1f-4155ae1f6395",
      "destination": "Paris",
      "total_cost": 1785.0,
      "created_at": "2025-06-27T09:34:25.205971",
      "status": "confirmed"
    }
  ],
  "error": null
}
```

## Frontend Integration Examples

### React/Next.js Example

```javascript
// Generate a travel plan
const generatePlan = async (destination, budget, userWallet) => {
  try {
    const response = await fetch('http://localhost:8000/generate_plan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        destination,
        budget,
        user_wallet: userWallet,
      }),
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating plan:', error);
    throw error;
  }
};

// Confirm a plan
const confirmPlan = async (planId, userWallet) => {
  try {
    const response = await fetch('http://localhost:8000/confirm_plan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        plan_id: planId,
        user_wallet: userWallet,
      }),
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error confirming plan:', error);
    throw error;
  }
};

// Get user plans
const getUserPlans = async (userWallet) => {
  try {
    const response = await fetch(`http://localhost:8000/get_user_plans/${userWallet}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching user plans:', error);
    throw error;
  }
};
```

### Vue.js Example

```javascript
// Composition API
import { ref } from 'vue';

export function useTravelAPI() {
  const plans = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const generatePlan = async (destination, budget, userWallet) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await fetch('http://localhost:8000/generate_plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          destination,
          budget,
          user_wallet: userWallet,
        }),
      });
      
      const data = await response.json();
      return data;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    plans,
    loading,
    error,
    generatePlan,
  };
}
```

### Angular Example

```typescript
// travel.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TravelService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  generatePlan(destination: string, budget: number, userWallet: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/generate_plan`, {
      destination,
      budget,
      user_wallet: userWallet
    });
  }

  confirmPlan(planId: string, userWallet: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/confirm_plan`, {
      plan_id: planId,
      user_wallet: userWallet
    });
  }

  getUserPlans(userWallet: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/get_user_plans/${userWallet}`);
  }
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "status": "error",
  "error": "Descriptive error message"
}
```

Common error scenarios:
- Invalid plan ID
- Budget exceeded
- Missing required fields
- Network errors

## Data Models

### FlightInfo
```typescript
interface FlightInfo {
  from_location: string;
  to_location: string;
  airline: string;
  dates: string;
  price: number;
}
```

### HotelInfo
```typescript
interface HotelInfo {
  name: string;
  location: string;
  price_per_night: number;
  nights: number;
  total: number;
}
```

### TravelPlan
```typescript
interface TravelPlan {
  destination: string;
  flights: FlightInfo[];
  hotels: HotelInfo[];
  activities: string[];
  total_cost: number;
  platform_fee: number;
  grand_total: number;
  plan_id: string;
  created_at: string;
}
```

## Production Considerations

1. **Database Integration**: Replace in-memory storage with a proper database (PostgreSQL, MongoDB)
2. **Authentication**: Implement JWT or OAuth2 authentication
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Caching**: Implement Redis caching for frequently accessed data
5. **Monitoring**: Add logging and monitoring (Prometheus, Grafana)
6. **Security**: Implement input validation and sanitization
7. **HTTPS**: Use HTTPS in production
8. **Environment Variables**: Use environment variables for configuration

## Testing

Test the API endpoints using curl:

```bash
# Generate a plan
curl -X POST http://localhost:8000/generate_plan \
  -H "Content-Type: application/json" \
  -d '{"destination": "Tokyo", "budget": 3000, "user_wallet": "0x1234567890abcdef"}'

# Confirm a plan
curl -X POST http://localhost:8000/confirm_plan \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "PLAN_ID_HERE", "user_wallet": "0x1234567890abcdef"}'

# Get user plans
curl -X GET "http://localhost:8000/get_user_plans/0x1234567890abcdef"
```

## Support

For API support or questions, please refer to the project documentation or create an issue in the repository. 