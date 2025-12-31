# Admin Settings API Documentation

## 📋 API Endpoints

All endpoints are under `/api/v1/settings` and require admin authentication.

### **Profile Management**
```
GET    /api/v1/settings/profile          # Get admin profile
PATCH  /api/v1/settings/profile          # Update admin profile
```

### **Password Management**
```
PATCH  /api/v1/settings/change-password  # Change password
```

### **Notification Preferences**
```
GET    /api/v1/settings/notifications    # Get notification preferences
PATCH  /api/v1/settings/notifications    # Update notification preferences
```

### **Combined Settings**
```
GET    /api/v1/settings/all              # Get all settings at once
```

---

## 👤 1. Profile Management

### 1.1 Get Admin Profile

**Endpoint:** `GET /api/v1/settings/profile`

**Response:**
```json
{
  "id": "uuid",
  "email": "admin@example.com",
  "full_name": "John Doe",
  "phone": "+91-9876543210",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

### 1.2 Update Admin Profile

**Endpoint:** `PATCH /api/v1/settings/profile`

**Request Body:**
```json
{
  "full_name": "John Smith",
  "phone": "+91-9876543211"
}
```

**Response:** Same as Get Profile

**Notes:**
- All fields are optional
- Email cannot be changed for security reasons
- Only provided fields will be updated

---

## 🔐 2. Password Management

### Change Password

**Endpoint:** `PATCH /api/v1/settings/change-password`

**Request Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (!@#$%^&*(),.?":{}|<>)

**Response:**
```json
{
  "id": "uuid",
  "email": "admin@example.com",
  "full_name": "John Doe",
  "role": "ADMIN",
  "is_active": true
}
```

**Error Responses:**
- `400` - Incorrect old password
- `400` - New password same as old password
- `400` - Password doesn't meet requirements

---

## 🔔 3. Notification Preferences

### 3.1 Get Notification Preferences

**Endpoint:** `GET /api/v1/settings/notifications`

**Response:**
```json
{
  "email_notifications": true,
  "subscription_reminders": true,
  "new_developer_alerts": true,
  "payment_alerts": true,
  "system_updates": true
}
```

**Notification Types:**
- `email_notifications` - General email notifications
- `subscription_reminders` - Alerts for expiring subscriptions
- `new_developer_alerts` - Notifications when new developers register
- `payment_alerts` - Payment and transaction notifications
- `system_updates` - System maintenance and update notifications

### 3.2 Update Notification Preferences

**Endpoint:** `PATCH /api/v1/settings/notifications`

**Request Body:**
```json
{
  "subscription_reminders": false,
  "payment_alerts": true
}
```

**Notes:**
- All fields are optional
- Only provided fields will be updated
- Defaults to `true` for new admins

**Response:** Same as Get Notification Preferences

---

## 📦 4. Get All Settings

**Endpoint:** `GET /api/v1/settings/all`

**Response:**
```json
{
  "profile": {
    "id": "uuid",
    "email": "admin@example.com",
    "full_name": "John Doe",
    "phone": "+91-9876543210",
    "role": "ADMIN",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  },
  "notifications": {
    "email_notifications": true,
    "subscription_reminders": true,
    "new_developer_alerts": true,
    "payment_alerts": true,
    "system_updates": true
  }
}
```

**Use Case:** Load entire settings page with one API call

---

## 💻 Usage Examples

### JavaScript/TypeScript

```typescript
const API_BASE = '/api/v1/settings';

// 1. Get Profile
async function getProfile() {
  const response = await fetch(`${API_BASE}/profile`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// 2. Update Profile
async function updateProfile(data) {
  const response = await fetch(`${API_BASE}/profile`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return response.json();
}

// 3. Change Password
async function changePassword(oldPassword, newPassword) {
  const response = await fetch(`${API_BASE}/change-password`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword
    })
  });
  return response.json();
}

// 4. Get Notification Preferences
async function getNotifications() {
  const response = await fetch(`${API_BASE}/notifications`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// 5. Update Notification Preferences
async function updateNotifications(preferences) {
  const response = await fetch(`${API_BASE}/notifications`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(preferences)
  });
  return response.json();
}

// 6. Get All Settings
async function getAllSettings() {
  const response = await fetch(`${API_BASE}/all`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

### Python

```python
import requests

API_BASE = "http://localhost:8000/api/v1/settings"
headers = {"Authorization": f"Bearer {token}"}

# 1. Get Profile
def get_profile():
    response = requests.get(f"{API_BASE}/profile", headers=headers)
    return response.json()

# 2. Update Profile
def update_profile(full_name=None, phone=None):
    data = {}
    if full_name:
        data["full_name"] = full_name
    if phone:
        data["phone"] = phone
    
    response = requests.patch(
        f"{API_BASE}/profile",
        headers=headers,
        json=data
    )
    return response.json()

# 3. Change Password
def change_password(old_password, new_password):
    response = requests.patch(
        f"{API_BASE}/change-password",
        headers=headers,
        json={
            "old_password": old_password,
            "new_password": new_password
        }
    )
    return response.json()

# 4. Get Notifications
def get_notifications():
    response = requests.get(f"{API_BASE}/notifications", headers=headers)
    return response.json()

# 5. Update Notifications
def update_notifications(**preferences):
    response = requests.patch(
        f"{API_BASE}/notifications",
        headers=headers,
        json=preferences
    )
    return response.json()

# 6. Get All Settings
def get_all_settings():
    response = requests.get(f"{API_BASE}/all", headers=headers)
    return response.json()
```

---

## 🎯 Common Workflows

### 1. Settings Page Load
```javascript
// Load all settings when page opens
async function loadSettingsPage() {
  const settings = await getAllSettings();
  
  // Populate form fields
  document.getElementById('fullName').value = settings.profile.full_name;
  document.getElementById('phone').value = settings.profile.phone || '';
  document.getElementById('email').value = settings.profile.email;
  
  // Set notification checkboxes
  document.getElementById('emailNotifs').checked = settings.notifications.email_notifications;
  document.getElementById('subReminders').checked = settings.notifications.subscription_reminders;
  document.getElementById('devAlerts').checked = settings.notifications.new_developer_alerts;
  document.getElementById('paymentAlerts').checked = settings.notifications.payment_alerts;
  document.getElementById('systemUpdates').checked = settings.notifications.system_updates;
}
```

### 2. Update Profile
```javascript
async function handleProfileUpdate(event) {
  event.preventDefault();
  
  const data = {
    full_name: document.getElementById('fullName').value,
    phone: document.getElementById('phone').value
  };
  
  try {
    const updated = await updateProfile(data);
    alert('Profile updated successfully!');
  } catch (error) {
    alert('Failed to update profile');
  }
}
```

### 3. Change Password
```javascript
async function handlePasswordChange(event) {
  event.preventDefault();
  
  const oldPassword = document.getElementById('oldPassword').value;
  const newPassword = document.getElementById('newPassword').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  
  if (newPassword !== confirmPassword) {
    alert('Passwords do not match');
    return;
  }
  
  try {
    await changePassword(oldPassword, newPassword);
    alert('Password changed successfully!');
    // Clear form
    event.target.reset();
  } catch (error) {
    alert(error.response?.data?.detail || 'Failed to change password');
  }
}
```

### 4. Toggle Notifications
```javascript
async function handleNotificationToggle(event) {
  const { name, checked } = event.target;
  
  try {
    await updateNotifications({ [name]: checked });
    console.log(`${name} updated to ${checked}`);
  } catch (error) {
    // Revert checkbox on error
    event.target.checked = !checked;
    alert('Failed to update notification preference');
  }
}
```

---

## 🔐 Security Notes

1. **Password Changes:**
   - Requires old password verification
   - Invalidates cache after change
   - Logs all password change attempts

2. **Profile Updates:**
   - Email cannot be changed (security)
   - All changes are logged
   - Cache is invalidated after updates

3. **Authentication:**
   - All endpoints require valid admin token
   - ADMIN or SUPER_ADMIN role required for notifications

---

## 📝 Quick Reference

| Endpoint | Method | Purpose | Admin Only |
|----------|--------|---------|------------|
| `/profile` | GET | Get profile | No |
| `/profile` | PATCH | Update profile | No |
| `/change-password` | PATCH | Change password | No |
| `/notifications` | GET | Get preferences | Yes |
| `/notifications` | PATCH | Update preferences | Yes |
| `/all` | GET | Get all settings | Yes |

---

## ✅ Implementation Complete

All admin settings features implemented:

✅ **Profile Management**
- View profile details
- Update name and phone
- Email protection

✅ **Password Management**
- Secure password change
- Strong password validation
- Old password verification

✅ **Notification Preferences**
- 5 notification types
- Granular control
- Default settings for new admins

✅ **Combined Settings API**
- Single call for all settings
- Optimized for settings page load

**Ready for production use!** 🎉
