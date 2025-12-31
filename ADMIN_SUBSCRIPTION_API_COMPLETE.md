# Admin Subscription API - Complete Reference

## 📋 Final API Endpoints

### **Statistics**
```
GET /api/v1/admin/subscriptions/stats
```

### **Subscription Plans (CRUD)**
```
GET    /api/v1/admin/subscriptions/plans          # List all plans
POST   /api/v1/admin/subscriptions/plans          # Create new plan
PUT    /api/v1/admin/subscriptions/plans/{id}     # Update plan
DELETE /api/v1/admin/subscriptions/plans/{id}     # Delete (deactivate) plan
```

### **Subscriptions**
```
GET /api/v1/admin/subscriptions/subscriptions     # List all subscriptions (paginated)
```

### **Notifications**
```
POST /api/v1/admin/subscriptions/send-renewal-reminders  # Send renewal reminder emails
```

---

## 📊 1. Get Statistics

**Endpoint:** `GET /api/v1/admin/subscriptions/stats`

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

## 📦 2. Subscription Plans Management

### 2.1 List All Plans

**Endpoint:** `GET /api/v1/admin/subscriptions/plans`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Annual Premium",
    "duration_days": 365,
    "price": 25000.00,
    "features": {
      "max_projects": 10,
      "team_access": true
    },
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### 2.2 Create Plan

**Endpoint:** `POST /api/v1/admin/subscriptions/plans`

**Request Body:**
```json
{
  "name": "Quarterly Basic",
  "duration_days": 90,
  "price": 7500.00,
  "features": {
    "max_projects": 5,
    "team_access": false
  },
  "is_active": true
}
```

**Response:** Same as plan object above

### 2.3 Update Plan

**Endpoint:** `PUT /api/v1/admin/subscriptions/plans/{plan_id}`

**Request Body:**
```json
{
  "name": "Annual Premium (Updated)",
  "duration_days": 365,
  "price": 30000.00,
  "features": {
    "max_projects": 15,
    "team_access": true,
    "priority_support": true
  },
  "is_active": true
}
```

**Response:** Updated plan object

### 2.4 Delete Plan

**Endpoint:** `DELETE /api/v1/admin/subscriptions/plans/{plan_id}`

**Response:**
```json
{
  "message": "Plan deactivated successfully",
  "plan_id": "uuid"
}
```

**Note:** 
- This is a **soft delete** - sets `is_active` to `false`
- Cannot delete if active subscriptions are using this plan
- Returns error with count if active subscriptions exist

---

## 📋 3. List Subscriptions (Paginated)

**Endpoint:** `GET /api/v1/admin/subscriptions/subscriptions`

**Query Parameters:**
- `status` (optional): ACTIVE | EXPIRED | CANCELLED | PENDING
- `skip` (optional, default: 0): Records to skip
- `limit` (optional, default: 50, max: 100): Records per page

**Response:**
```json
{
  "total": 150,
  "skip": 0,
  "limit": 50,
  "data": [
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
      "auto_renewal": true,
      "created_at": "2025-01-01T10:30:00Z"
    }
  ]
}
```

---

## 🔐 Authentication

All endpoints require **Admin** role:
```
Authorization: Bearer <admin_token>
```

---

## 💻 Complete Usage Examples

### JavaScript/TypeScript

```typescript
const API_BASE = '/api/v1/admin/subscriptions';

// 1. Get Statistics
async function getStats() {
  const response = await fetch(`${API_BASE}/stats`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// 2. List Plans
async function listPlans() {
  const response = await fetch(`${API_BASE}/plans`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// 3. Create Plan
async function createPlan(planData) {
  const response = await fetch(`${API_BASE}/plans`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(planData)
  });
  return response.json();
}

// 4. Update Plan
async function updatePlan(planId, planData) {
  const response = await fetch(`${API_BASE}/plans/${planId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(planData)
  });
  return response.json();
}

// 5. Delete Plan
async function deletePlan(planId) {
  const response = await fetch(`${API_BASE}/plans/${planId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// 6. List Subscriptions (with pagination)
async function listSubscriptions(page = 1, pageSize = 50, status = null) {
  const skip = (page - 1) * pageSize;
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: pageSize.toString()
  });
  
  if (status) params.append('status', status);
  
  const response = await fetch(`${API_BASE}/subscriptions?${params}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

### Python

```python
import requests

API_BASE = "http://localhost:8000/api/v1/admin/subscriptions"
headers = {"Authorization": f"Bearer {token}"}

# 1. Get Statistics
def get_stats():
    response = requests.get(f"{API_BASE}/stats", headers=headers)
    return response.json()

# 2. List Plans
def list_plans():
    response = requests.get(f"{API_BASE}/plans", headers=headers)
    return response.json()

# 3. Create Plan
def create_plan(plan_data):
    response = requests.post(
        f"{API_BASE}/plans",
        headers=headers,
        json=plan_data
    )
    return response.json()

# 4. Update Plan
def update_plan(plan_id, plan_data):
    response = requests.put(
        f"{API_BASE}/plans/{plan_id}",
        headers=headers,
        json=plan_data
    )
    return response.json()

# 5. Delete Plan
def delete_plan(plan_id):
    response = requests.delete(
        f"{API_BASE}/plans/{plan_id}",
        headers=headers
    )
    return response.json()

# 6. List Subscriptions
def list_subscriptions(skip=0, limit=50, status=None):
    params = {"skip": skip, "limit": limit}
    if status:
        params["status"] = status
    
    response = requests.get(
        f"{API_BASE}/subscriptions",
        headers=headers,
        params=params
    )
    return response.json()
```

---

## 🎯 Common Workflows

### 1. Dashboard Overview
```javascript
// Fetch stats for dashboard cards
const stats = await getStats();

// Display:
// - Active: stats.total_active
// - Expiring Soon: stats.expiring_soon
// - Expired: stats.expired
// - Monthly Revenue: stats.monthly_revenue
```

### 2. Manage Plans
```javascript
// List all plans
const plans = await listPlans();

// Create new plan
const newPlan = await createPlan({
  name: "Enterprise",
  duration_days: 365,
  price: 50000,
  features: { max_projects: 50, team_access: true },
  is_active: true
});

// Update plan price
await updatePlan(planId, {
  ...existingPlan,
  price: 35000
});

// Delete plan
await deletePlan(planId);
```

### 3. View Subscriptions
```javascript
// Get first page of active subscriptions
const result = await listSubscriptions(1, 50, 'ACTIVE');

// Display table with result.data
// Show pagination: Page 1 of Math.ceil(result.total / result.limit)
```

---

## ⚠️ Important Notes

### Plan Deletion
- **Soft Delete Only**: Plans are deactivated (`is_active = false`), not permanently deleted
- **Protection**: Cannot delete plans with active subscriptions
- **Error Handling**: Returns 400 error with count of active subscriptions if deletion blocked

### Pagination
- **Default**: 50 records per page
- **Maximum**: 100 records per page
- **Total Count**: Always included in response for UI pagination

### Status Values
- `ACTIVE` - Currently active subscription
- `EXPIRED` - Subscription has ended
- `CANCELLED` - Subscription was cancelled
- `PENDING` - Payment pending

---

## 📝 Quick Reference Table

| Endpoint | Method | Purpose | Pagination |
|----------|--------|---------|------------|
| `/stats` | GET | Get statistics | No |
| `/plans` | GET | List all plans | No |
| `/plans` | POST | Create plan | No |
| `/plans/{id}` | PUT | Update plan | No |
| `/plans/{id}` | DELETE | Delete plan | No |
| `/subscriptions` | GET | List subscriptions | Yes |

---

## 🚀 Testing

1. **Start server:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Open API docs:**
   ```
   http://localhost:8000/docs
   ```

3. **Navigate to "Admin - Subscriptions" section**

4. **Test all endpoints with your admin token**

---

## ✅ Implementation Complete

All requested features implemented:

✅ **Statistics API**
- Total Active
- Expiring Soon
- Expired
- Monthly Revenue
- Total Revenue

✅ **Subscription Details API**
- Developer Name & Email
- Plan Name & Price
- Start/End Dates
- Days Left
- Status
- Auto Renewal
- **Pagination Support**

✅ **Plan Management (CRUD)**
- Create Plan
- List Plans
- Update Plan
- Delete Plan (with protection)

✅ **Renewal Reminders**
- Send email notifications to developers
- Customizable expiry threshold
- Detailed success/failure reporting

---

## 📧 4. Send Renewal Reminders

**Endpoint:** `POST /api/v1/admin/subscriptions/send-renewal-reminders`

**Query Parameters:**
- `days_threshold` (optional, default: 7, max: 30): Send reminders for subscriptions expiring within N days

**Response:**
```json
{
  "message": "Renewal reminders processed for subscriptions expiring within 7 days",
  "days_threshold": 7,
  "total_found": 5,
  "emails_sent": 4,
  "emails_failed": 1,
  "reminders": [
    {
      "developer_id": "uuid",
      "developer_name": "ABC Developers",
      "email": "dev@example.com",
      "plan_name": "Annual Premium",
      "days_left": 5,
      "end_date": "2026-01-05T00:00:00Z",
      "status": "sent"
    },
    {
      "developer_id": "uuid",
      "developer_name": "XYZ Ltd",
      "status": "failed",
      "reason": "No email address found"
    }
  ]
}
```

**Email Template Features:**
- Professional HTML design
- Subscription details (plan, expiry date, days left, price)
- Clear call-to-action button
- Plain text fallback
- Branded footer

**Usage Example:**

```javascript
// Send reminders for subscriptions expiring in 7 days
async function sendRenewalReminders(daysThreshold = 7) {
  const response = await fetch(
    `/api/v1/admin/subscriptions/send-renewal-reminders?days_threshold=${daysThreshold}`,
    {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return response.json();
}

// Usage
const result = await sendRenewalReminders(7);
console.log(`Sent ${result.emails_sent} reminders, ${result.emails_failed} failed`);
```

**Python Example:**

```python
def send_renewal_reminders(days_threshold=7):
    response = requests.post(
        f"{API_BASE}/send-renewal-reminders",
        headers=headers,
        params={"days_threshold": days_threshold}
    )
    return response.json()

# Usage
result = send_renewal_reminders(7)
print(f"Sent {result['emails_sent']} reminders")
```

**Workflow Integration:**

```javascript
// 4. Send Renewal Reminders Workflow
async function sendRemindersWorkflow() {
  // Step 1: Check stats first
  const stats = await getStats();
  
  if (stats.expiring_soon > 0) {
    console.log(`Found ${stats.expiring_soon} subscriptions expiring soon`);
    
    // Step 2: Send reminders
    const result = await sendRenewalReminders(7);
    
    // Step 3: Display results
    console.log(`✅ Sent: ${result.emails_sent}`);
    console.log(`❌ Failed: ${result.emails_failed}`);
    
    // Step 4: Show details
    result.reminders.forEach(reminder => {
      if (reminder.status === 'sent') {
        console.log(`✓ ${reminder.developer_name} - ${reminder.days_left} days left`);
      } else {
        console.log(`✗ ${reminder.developer_name} - ${reminder.reason}`);
      }
    });
  }
}
```

---

**Ready for production use!** 🎉
