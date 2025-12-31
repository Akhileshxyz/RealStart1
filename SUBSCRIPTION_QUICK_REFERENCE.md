# Admin Subscription API - Quick Reference

## 📊 API Endpoints Overview

```
/api/v1/admin/subscriptions/
├── GET /stats                      # Subscription statistics
├── GET /subscriptions              # All subscriptions (detailed)
│   └── ?status=ACTIVE|EXPIRED|CANCELLED|PENDING
├── GET /plans                      # All subscription plans
├── POST /plans                     # Create new plan
├── GET /notifications/expiry       # Expiring subscriptions
└── GET /analytics/revenue          # Revenue analytics
```

---

## 🎯 Quick Usage

### Get Statistics for Dashboard
```bash
GET /api/v1/admin/subscriptions/stats
```

**Response:**
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

---

### Get Detailed Subscriptions
```bash
# All subscriptions
GET /api/v1/admin/subscriptions/subscriptions

# Only active subscriptions
GET /api/v1/admin/subscriptions/subscriptions?status=ACTIVE

# Only expired subscriptions
GET /api/v1/admin/subscriptions/subscriptions?status=EXPIRED
```

**Response:**
```json
[
  {
    "id": "uuid",
    "developer_name": "ABC Developers",
    "developer_email": "dev@example.com",
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

---

## 📋 Data Fields Mapping

| UI Display | API Field | Description |
|------------|-----------|-------------|
| Developer | `developer_name` | Company/Developer name |
| Email | `developer_email` | Contact email |
| Plan | `plan_name` | Subscription plan name |
| Price | `plan_price` | Plan cost |
| Start Date | `start_date` | When subscription started |
| End Date | `end_date` | When subscription ends |
| Days Left | `days_left` | Remaining days |
| Status | `status` | ACTIVE/EXPIRED/CANCELLED/PENDING |
| Auto Renewal | `auto_renewal` | true/false |

---

## 🎨 UI Implementation Guide

### Dashboard Cards
```
┌─────────────────────────────────────────────────────────┐
│  Subscription Overview                                   │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Active       │  │ Expiring     │  │ Expired      │  │
│  │ 25           │  │ 3 ⚠️         │  │ 10           │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────────────────┐  ┌──────────────────────┐│
│  │ Monthly Revenue          │  │ Total Revenue         ││
│  │ ₹50,000                  │  │ ₹2,50,000            ││
│  └──────────────────────────┘  └──────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Subscriptions Table
```
┌────────────────────────────────────────────────────────────────────────────┐
│  Subscriptions Management                                    [Filter: All ▼]│
├────────────────────────────────────────────────────────────────────────────┤
│ Developer    │ Plan      │ Start Date │ End Date   │ Days Left │ Status    │
├──────────────┼───────────┼────────────┼────────────┼───────────┼───────────┤
│ ABC Dev      │ Annual    │ 2025-01-01 │ 2026-01-01 │ 365       │ 🟢 ACTIVE │
│ XYZ Ltd      │ Quarterly │ 2024-12-01 │ 2025-03-01 │ 5 ⚠️     │ 🟢 ACTIVE │
│ DEF Inc      │ Annual    │ 2024-01-01 │ 2025-01-01 │ 0         │ 🔴 EXPIRED│
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Authorization

All endpoints require **Admin** authentication:
- Role: `ADMIN` or `SUPER_ADMIN`
- Header: `Authorization: Bearer <token>`

---

## 💡 Implementation Tips

### 1. Dashboard Stats
```javascript
// Fetch stats on page load
useEffect(() => {
  fetchStats();
}, []);

const fetchStats = async () => {
  const response = await fetch('/api/v1/admin/subscriptions/stats', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  setStats(data);
};
```

### 2. Subscription Table
```javascript
// Fetch details with optional filter
const fetchSubscriptions = async (status = null) => {
  const url = status 
    ? `/api/v1/admin/subscriptions/subscriptions?status=${status}`
    : '/api/v1/admin/subscriptions/subscriptions';
    
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  setSubscriptions(data);
};
```

### 3. Status Badge Colors
```javascript
const getStatusBadge = (status) => {
  const colors = {
    'ACTIVE': 'green',
    'EXPIRED': 'red',
    'CANCELLED': 'gray',
    'PENDING': 'yellow'
  };
  return colors[status] || 'gray';
};
```

### 4. Expiring Soon Alert
```javascript
// Highlight subscriptions expiring within 7 days
const isExpiringSoon = (subscription) => {
  return subscription.status === 'ACTIVE' && subscription.days_left <= 7;
};
```

---

## 🚀 Testing

1. **Start the server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Open API docs**
   ```
   http://localhost:8000/docs
   ```

3. **Navigate to "Admin - Subscriptions" section**

4. **Authenticate with admin token**

5. **Test endpoints:**
   - Try `/stats` endpoint
   - Try `/details` endpoint
   - Try `/details?status=ACTIVE` endpoint

---

## 📝 Status Values

| Status | Description | UI Display |
|--------|-------------|------------|
| `ACTIVE` | Subscription is currently active | 🟢 Green badge |
| `EXPIRED` | Subscription has expired | 🔴 Red badge |
| `CANCELLED` | Subscription was cancelled | ⚫ Gray badge |
| `PENDING` | Payment pending | 🟡 Yellow badge |

---

## 🎯 Common Use Cases

### 1. Send Renewal Reminders
```javascript
// Get subscriptions expiring within 7 days
const expiring = subscriptions.filter(sub => 
  sub.status === 'ACTIVE' && sub.days_left <= 7
);

// Send email to each
expiring.forEach(sub => {
  sendRenewalEmail(sub.developer_email, sub);
});
```

### 2. Revenue Report
```javascript
// Display monthly vs total revenue
const stats = await fetchStats();
const growth = ((stats.monthly_revenue / stats.total_revenue) * 100).toFixed(2);
console.log(`This month is ${growth}% of total revenue`);
```

### 3. Filter Active Subscriptions
```javascript
// Show only active subscriptions in table
const activeOnly = await fetchSubscriptions('ACTIVE');
```

---

## 📚 Related Documentation

- Full API Documentation: `ADMIN_SUBSCRIPTION_API.md`
- Implementation Details: `SUBSCRIPTION_IMPLEMENTATION_SUMMARY.md`
- Main API Reference: `API_REFERENCE.md.resolved`
