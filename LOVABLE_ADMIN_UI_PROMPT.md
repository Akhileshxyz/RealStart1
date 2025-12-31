# RealStart Admin Dashboard - Lovable UI Prompts

## 🎯 Project Overview

Create a modern, professional admin dashboard for RealStart - a real estate platform management system. The dashboard should be built with React, TypeScript, and Tailwind CSS with a focus on clean design, excellent UX, and comprehensive data visualization.

**Important:** Use the existing RealStart UI design system, colors, and component styles. Do not create a new color palette - maintain consistency with the current frontend.

---

## 📱 Layout Structure

### 1. Sidebar Navigation
```
┌─────────────────────┐
│  RealStart Logo     │
├─────────────────────┤
│ 📊 Dashboard        │
│ 📋 Subscriptions    │
│ 👥 Developers       │
│ 👤 Users            │
│ 🏢 Projects         │
│ 📍 Landmarks        │
│ 📹 Videos           │
│ 📢 Ads              │
│ 👨‍💼 Team            │
│ 📈 Analytics        │
│ ⚙️  Settings        │
├─────────────────────┤
│ 👤 Admin Profile    │
│ 🚪 Logout           │
└─────────────────────┘
```

**Features:**
- Collapsible on mobile
- Active state highlighting
- Icons for each menu item
- User profile at bottom
- Smooth transitions

### 2. Top Bar
```
┌──────────────────────────────────────────────────────────┐
│  [☰ Menu]  RealStart Admin    [🔍 Search]  [🔔] [👤]   │
└──────────────────────────────────────────────────────────┘
```

**Features:**
- Breadcrumb navigation
- Global search
- Notifications dropdown
- User menu dropdown

---

## 📄 Page Specifications

## 1. Dashboard Page (`/dashboard`)

### API Endpoint
```
GET /api/v1/admin/dashboard
GET /api/v1/admin/system-health
```

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Dashboard                                    [Refresh] │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Total    │  │ Active   │  │ Revenue  │  │ New      ││
│  │ Users    │  │ Subs     │  │ This     │  │ Devs     ││
│  │ 1,234    │  │ 45       │  │ Month    │  │ This     ││
│  │ +12%     │  │ -2       │  │ ₹2.5L    │  │ Week: 5  ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
├─────────────────────────────────────────────────────────┤
│  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │ Revenue Chart      │  │ System Health            │  │
│  │ (Line/Bar Chart)   │  │ • API: ✅ Healthy        │  │
│  │                    │  │ • DB: ✅ Connected       │  │
│  │                    │  │ • Redis: ✅ Active       │  │
│  └────────────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  Recent Activity                                        │
│  • New developer registered: ABC Ltd                    │
│  • Subscription expiring: XYZ Corp (5 days)            │
│  • Project approved: Green Valley                       │
└─────────────────────────────────────────────────────────┘
```

**Components Needed:**
- Stat cards with trend indicators
- Line/Bar chart for revenue
- System health status indicators
- Activity feed/timeline
- Refresh button

---

## 2. Subscriptions Page (`/subscriptions`)

### API Endpoints
```
GET /api/v1/admin/subscriptions/stats
GET /api/v1/admin/subscriptions/subscriptions?skip=0&limit=50&status=ACTIVE
POST /api/v1/admin/subscriptions/send-renewal-reminders?days_threshold=7
GET /api/v1/admin/subscriptions/plans
POST /api/v1/admin/subscriptions/plans
PUT /api/v1/admin/subscriptions/plans/{id}
DELETE /api/v1/admin/subscriptions/plans/{id}
```

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Subscriptions                    [+ New Plan] [Send    │
│                                              Reminders] │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Active   │  │ Expiring │  │ Expired  │  │ Monthly  ││
│  │ 25       │  │ Soon: 3  │  │ 10       │  │ Revenue  ││
│  │          │  │ ⚠️       │  │          │  │ ₹50,000  ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
├─────────────────────────────────────────────────────────┤
│  [All ▼] [Status Filter ▼]              [Search...]    │
├─────────────────────────────────────────────────────────┤
│  Developer    │ Plan      │ End Date   │ Days │ Status │
│  ABC Dev      │ Annual    │ 2026-01-01 │ 365  │ 🟢     │
│  XYZ Ltd      │ Quarterly │ 2025-03-01 │ 5⚠️  │ 🟢     │
│  DEF Inc      │ Annual    │ 2025-01-01 │ 0    │ 🔴     │
├─────────────────────────────────────────────────────────┤
│  ← Previous  Page 1 of 5  Next →                       │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Stats cards at top
- Filter by status dropdown
- Search functionality
- Pagination
- Status badges (green/yellow/red)
- Action buttons (Send Reminders)
- Modal for creating/editing plans

**Modals:**
1. **Create/Edit Plan Modal**
   - Plan name input
   - Duration (days) input
   - Price input
   - Features (JSON editor or key-value pairs)
   - Active toggle

2. **Send Reminders Modal**
   - Days threshold slider (1-30)
   - Preview of affected subscriptions
   - Confirm button
   - Results display after sending

---

## 3. Developers Page (`/developers`)

### API Endpoints
```
GET /api/v1/admin/developers/
POST /api/v1/admin/developers/
GET /api/v1/admin/developers/{id}
PUT /api/v1/admin/developers/{id}
DELETE /api/v1/admin/developers/{id}
POST /api/v1/admin/developers/{id}/impersonate
```

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Developers                              [+ Add Developer]│
├─────────────────────────────────────────────────────────┤
│  [Search by name...]                    [Filter ▼]      │
├─────────────────────────────────────────────────────────┤
│  Name        │ Email          │ Projects │ Status │ ... │
│  ABC Dev     │ abc@dev.com    │ 5        │ ✅     │ ⋮  │
│  XYZ Ltd     │ xyz@ltd.com    │ 3        │ ✅     │ ⋮  │
│  DEF Inc     │ def@inc.com    │ 0        │ ⏸️     │ ⋮  │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Search and filter
- Table with developer info
- Action menu (⋮) with:
  - View Details
  - Edit
  - Impersonate
  - Suspend/Activate
  - Delete
- Modal for add/edit developer

---

## 4. Users Page (`/users`)

### API Endpoints
```
GET /api/v1/admin/users/
POST /api/v1/admin/users/
GET /api/v1/admin/users/{id}
PUT /api/v1/admin/users/{id}
DELETE /api/v1/admin/users/{id}
PATCH /api/v1/admin/users/{id}/suspend
PATCH /api/v1/admin/users/{id}/activate
```

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Users                                    [+ Add User]  │
├─────────────────────────────────────────────────────────┤
│  [Search...]  [Role: All ▼]  [Status: All ▼]          │
├─────────────────────────────────────────────────────────┤
│  Name      │ Email          │ Role   │ Status │ Actions│
│  John Doe  │ john@mail.com  │ BUYER  │ Active │ ⋮     │
│  Jane Doe  │ jane@mail.com  │ ADMIN  │ Active │ ⋮     │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Multi-filter (role, status)
- User management actions
- Suspend/Activate toggle
- Role badges with colors

---

## 5. Projects Page (`/projects`)

### API Endpoints
```
GET /api/v1/admin/projects/
GET /api/v1/admin/projects/{id}/details
PATCH /api/v1/admin/projects/{id}/approve
PATCH /api/v1/admin/projects/{id}/reject
POST /api/v1/admin/projects/{id}/communication
GET /api/v1/admin/projects/{id}/communication
GET /api/v1/admin/projects/change-requests/
POST /api/v1/admin/projects/change-requests/{id}/approve
POST /api/v1/admin/projects/change-requests/{id}/reject
```

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Projects                                               │
├─────────────────────────────────────────────────────────┤
│  [Pending ▼]  [Search...]                              │
├─────────────────────────────────────────────────────────┤
│  Project Name  │ Developer │ Location │ Status │ Actions│
│  Green Valley  │ ABC Dev   │ Bangalore│ Pending│ ⋮     │
│  Blue Heights  │ XYZ Ltd   │ Mumbai   │ Approved│⋮     │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Status filter (Pending, Approved, Rejected)
- Project details modal/page
- Approve/Reject buttons
- Communication log
- Change requests tab

---

## 6. Settings Page (`/settings`)

### API Endpoints
```
GET /api/v1/settings/all
PATCH /api/v1/settings/profile
PATCH /api/v1/settings/change-password
GET /api/v1/settings/notifications
PATCH /api/v1/settings/notifications
```

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Settings                                               │
├─────────────────────────────────────────────────────────┤
│  [Profile] [Password] [Notifications]                  │
├─────────────────────────────────────────────────────────┤
│  Profile Tab:                                           │
│  Full Name:    [John Doe..................]            │
│  Email:        admin@example.com (cannot change)       │
│  Phone:        [+91-9876543210............]            │
│                                    [Update Profile]     │
├─────────────────────────────────────────────────────────┤
│  Password Tab:                                          │
│  Old Password:     [..................]                 │
│  New Password:     [..................]                 │
│  Confirm Password: [..................]                 │
│                                    [Change Password]    │
├─────────────────────────────────────────────────────────┤
│  Notifications Tab:                                     │
│  ☑ Email Notifications                                 │
│  ☑ Subscription Reminders                              │
│  ☑ New Developer Alerts                                │
│  ☑ Payment Alerts                                      │
│  ☑ System Updates                                      │
│                                    [Save Preferences]   │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Tabbed interface
- Form validation
- Password strength indicator
- Toggle switches for notifications
- Success/error toast messages

---

## 7. Analytics Page (`/analytics`)

### API Endpoints
```
GET /api/v1/admin/analytics/cities
GET /api/v1/admin/analytics/landmarks
GET /api/v1/admin/analytics/growth
GET /api/v1/admin/analytics/demographics
GET /api/v1/admin/analytics/funnel
```

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Analytics                        [Date Range: Last 30d]│
├─────────────────────────────────────────────────────────┤
│  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │ Growth Metrics     │  │ User Demographics        │  │
│  │ (Line Chart)       │  │ (Pie Chart)              │  │
│  └────────────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │ City Analytics     │  │ Funnel Conversion        │  │
│  │ (Bar Chart)        │  │ (Funnel Chart)           │  │
│  └────────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Multiple chart types (Line, Bar, Pie, Funnel)
- Date range selector
- Export data button
- Interactive charts with tooltips

---

## 🛠️ Technical Requirements

### State Management
```typescript
// Use React Context or Zustand for global state
interface AdminState {
  user: AdminUser | null;
  isAuthenticated: boolean;
  notifications: Notification[];
  sidebarOpen: boolean;
}
```

### API Integration
```typescript
// Create API client with axios
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Authentication Flow
```typescript
// Login page
POST /api/v1/admin/login
{
  "email": "admin@example.com",
  "password": "password"
}

// Store token
localStorage.setItem('adminToken', response.access_token);

// Protected routes
<Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
```

---

## 📦 Component Library

### Reusable Components

1. **StatCard**
   ```tsx
   <StatCard
     title="Total Users"
     value="1,234"
     change="+12%"
     trend="up"
     icon={<UsersIcon />}
   />
   ```

2. **DataTable**
   ```tsx
   <DataTable
     columns={columns}
     data={data}
     pagination
     searchable
     onRowClick={handleRowClick}
   />
   ```

3. **Modal**
   ```tsx
   <Modal
     isOpen={isOpen}
     onClose={handleClose}
     title="Create Plan"
   >
     <Form />
   </Modal>
   ```

4. **StatusBadge**
   ```tsx
   <StatusBadge status="active" />
   <StatusBadge status="pending" />
   <StatusBadge status="expired" />
   ```

5. **ActionMenu**
   ```tsx
   <ActionMenu
     items={[
       { label: 'Edit', onClick: handleEdit },
       { label: 'Delete', onClick: handleDelete, danger: true }
     ]}
   />
   ```

---

## 🎯 Key Features to Implement

### 1. Real-time Updates
- WebSocket connection for live notifications
- Auto-refresh for dashboard stats
- Toast notifications for actions

### 2. Search & Filters
- Global search in top bar
- Per-page filters
- Advanced filter modals

### 3. Pagination
- Server-side pagination
- Page size selector (25, 50, 100)
- Jump to page input

### 4. Data Visualization
- Charts using Recharts or Chart.js
- Interactive tooltips
- Export to CSV/PDF

### 5. Responsive Design
- Mobile-friendly sidebar (drawer)
- Responsive tables (horizontal scroll)
- Touch-friendly buttons

### 6. Error Handling
- API error boundaries
- Retry mechanisms
- User-friendly error messages

### 7. Loading States
- Skeleton loaders
- Spinner for actions
- Progress bars for uploads

---

## 🚀 Implementation Steps

### Phase 1: Setup & Authentication
1. Create React app with TypeScript
2. Setup Tailwind CSS
3. Create login page
4. Implement authentication
5. Setup routing

### Phase 2: Core Layout
1. Create sidebar navigation
2. Create top bar
3. Setup protected routes
4. Add logout functionality

### Phase 3: Dashboard
1. Fetch dashboard stats
2. Create stat cards
3. Add charts
4. Implement system health

### Phase 4: Subscriptions
1. Create subscriptions table
2. Add filters and search
3. Implement pagination
4. Create plan management modals
5. Add send reminders feature

### Phase 5: Other Pages
1. Developers management
2. Users management
3. Projects management
4. Settings page
5. Analytics page

### Phase 6: Polish
1. Add loading states
2. Error handling
3. Toast notifications
4. Responsive design
5. Performance optimization

---

## 📝 Example Code Snippets

### Login Page
```tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from './api';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await api.post('/admin/login', { email, password });
      localStorage.setItem('adminToken', response.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-6">Admin Login</h2>
        {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>}
        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 border rounded mb-4"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 border rounded mb-4"
          />
          <button className="w-full bg-indigo-600 text-white p-3 rounded hover:bg-indigo-700">
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
```

### Dashboard Stats
```tsx
import { useEffect, useState } from 'react';
import { api } from './api';

export function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/admin/dashboard');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Total Users" value={stats.total_users} />
        <StatCard title="Active Subscriptions" value={stats.active_subscriptions} />
        <StatCard title="Monthly Revenue" value={`₹${stats.monthly_revenue}`} />
        <StatCard title="New Developers" value={stats.new_developers} />
      </div>
    </div>
  );
}
```

---

## ✅ Checklist

- [ ] Authentication (Login/Logout)
- [ ] Dashboard with stats
- [ ] Subscriptions management
- [ ] Developers management
- [ ] Users management
- [ ] Projects approval
- [ ] Settings (Profile, Password, Notifications)
- [ ] Analytics charts
- [ ] Responsive design
- [ ] Error handling
- [ ] Loading states
- [ ] Toast notifications
- [ ] Search & filters
- [ ] Pagination
- [ ] Data export

---

## 🎨 Design Inspiration

**Similar Dashboards:**
- Stripe Dashboard
- Vercel Dashboard
- Linear App
- Notion

**Key Principles:**
- Clean and minimal
- Data-first approach
- Fast and responsive
- Intuitive navigation
- Professional appearance

---

## 📋 Additional Pages (Optional/Future)

The following pages have APIs available but can be implemented in later phases:

### 8. Landmarks Page (`/landmarks`)
**APIs:** POST, GET, PUT, DELETE `/api/v1/admin/landmarks`
- Create/edit landmarks
- List all landmarks
- Performance metrics
- Top performing landmarks

### 9. Videos Page (`/videos`)
**APIs:** GET, POST, DELETE `/api/v1/admin/videos`
- Upload videos
- List all videos
- Video analytics
- Delete videos

### 10. Ads Page (`/ads`)
**APIs:** 
- Internal ads: GET, POST, PUT, DELETE `/api/v1/admin/ads/internal`
- Meta ads: GET `/api/v1/admin/ads/meta`
- Google ads: GET `/api/v1/admin/ads/google`

### 11. Team Page (`/team`)
**APIs:** GET, POST, DELETE `/api/v1/admin/team`
- List team members
- Create team member
- Assign tasks
- Share clients

**Note:** These pages can use similar patterns to the main pages (table, search, filters, modals).

---

**Ready to build!** Use this prompt with Lovable.dev to create a complete admin dashboard. 🚀
