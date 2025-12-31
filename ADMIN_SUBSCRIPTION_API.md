# Admin Subscription API Documentation

## Overview
This document describes the enhanced Admin Subscription API endpoints that provide comprehensive subscription statistics and detailed subscription information.

## Base URL
```
/api/v1/admin/subscriptions
```

## Authentication
All endpoints require admin authentication (ADMIN or SUPER_ADMIN role).

---

## Endpoints

### 1. Get Subscription Statistics
Get comprehensive subscription statistics including active, expiring, expired counts, and revenue data.

**Endpoint:** `GET /api/v1/admin/subscriptions/stats`

**Response Schema:**
```json
{
  "total_active": 25,
  "expiring_soon": 3,
  "expired": 10,
  "monthly_revenue": 50000.00,
  "total_revenue": 250000.00,
  "total_subscriptions": 38
}
```

**Response Fields:**
- `total_active` (int): Number of currently active subscriptions
- `expiring_soon` (int): Number of subscriptions expiring within 7 days
- `expired` (int): Number of expired subscriptions
- `monthly_revenue` (float): Revenue from subscriptions started this month
- `total_revenue` (float): Total revenue from all active and expired subscriptions
- `total_subscriptions` (int): Total count of all subscriptions (including cancelled)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/subscriptions/stats" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

### 2. Get All Subscriptions (Detailed Information)
Get comprehensive information about all subscriptions including developer details, plan information, dates, and status.

**Endpoint:** `GET /api/v1/admin/subscriptions/subscriptions`

**Query Parameters:**
- `status` (optional): Filter by subscription status (ACTIVE, EXPIRED, CANCELLED, PENDING)

**Response Schema:**
```json
[
  {
    "id": "uuid-string",
    "developer_name": "ABC Developers",
    "developer_email": "developer@example.com",
    "plan_name": "Annual Premium",
    "plan_price": 25000.00,
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2026-01-01T00:00:00Z",
    "days_left": 365,
    "status": "ACTIVE",
    "auto_renewal": false,
    "created_at": "2025-01-01T10:30:00Z"
  }
]
```

**Response Fields:**
- `id` (UUID): Subscription ID
- `developer_name` (string): Name of the developer/company
- `developer_email` (string): Email of the developer account
- `plan_name` (string): Name of the subscription plan
- `plan_price` (float): Price of the plan
- `start_date` (datetime): Subscription start date
- `end_date` (datetime): Subscription end date
- `days_left` (int): Number of days remaining (0 for expired/cancelled)
- `status` (string): Current subscription status
- `auto_renewal` (boolean): Whether auto-renewal is enabled
- `created_at` (datetime): When the subscription was created

**Example Requests:**

Get all subscriptions:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/subscriptions/subscriptions" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Get only active subscriptions:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/subscriptions/subscriptions?status=ACTIVE" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Get expired subscriptions:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/subscriptions/subscriptions?status=EXPIRED" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Subscription Status Values
- `ACTIVE`: Subscription is currently active
- `EXPIRED`: Subscription has expired
- `CANCELLED`: Subscription was cancelled
- `PENDING`: Subscription payment is pending

---

## Use Cases

### Dashboard Overview
Use the `/stats` endpoint to display summary cards on the admin dashboard:
- Total Active Subscriptions
- Expiring Soon (action required)
- Expired Subscriptions
- Monthly Revenue
- Total Revenue

### Subscription Management Table
Use the `/details` endpoint to display a comprehensive table with:
- Developer information
- Plan details
- Important dates
- Days remaining
- Current status
- Auto-renewal status

Filter by status to create separate views for:
- Active subscriptions
- Expiring subscriptions (filter ACTIVE and check days_left < 7)
- Expired subscriptions
- Pending payments

---

## Frontend Integration Example

### React/TypeScript Example

```typescript
interface SubscriptionStats {
  total_active: number;
  expiring_soon: number;
  expired: number;
  monthly_revenue: number;
  total_revenue: number;
  total_subscriptions: number;
}

interface DetailedSubscription {
  id: string;
  developer_name: string;
  developer_email: string;
  plan_name: string;
  plan_price: number;
  start_date: string;
  end_date: string;
  days_left: number;
  status: 'ACTIVE' | 'EXPIRED' | 'CANCELLED' | 'PENDING';
  auto_renewal: boolean;
  created_at: string;
}

// Fetch subscription stats
const fetchStats = async (): Promise<SubscriptionStats> => {
  const response = await fetch('/api/v1/admin/subscriptions/stats', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
};

// Fetch detailed subscriptions
const fetchSubscriptions = async (
  status?: string
): Promise<DetailedSubscription[]> => {
  const url = status 
    ? `/api/v1/admin/subscriptions/subscriptions?status=${status}`
    : '/api/v1/admin/subscriptions/subscriptions';
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
};
```

---

## Notes

### Auto Renewal
The `auto_renewal` field has been added to the `DeveloperSubscription` model and will be properly tracked. You can implement auto-renewal logic in the developer portal to allow developers to enable/disable this feature.

### Days Left Calculation
- For ACTIVE subscriptions: Shows actual days remaining until end_date
- For EXPIRED/CANCELLED subscriptions: Always shows 0

### Revenue Calculation
- `total_revenue`: Sum of all ACTIVE and EXPIRED subscription prices
- `monthly_revenue`: Sum of subscription prices that started in the current month (and are ACTIVE or EXPIRED)

### Expiring Soon
Subscriptions are considered "expiring soon" if they are ACTIVE and their end_date is within the next 7 days.

---

## Testing

You can test these endpoints using the FastAPI documentation at:
```
http://localhost:8000/docs
```

Look for the "Admin - Subscriptions" section in the API documentation.
