# Admin Analytics API - Complete Reference

## 📊 Single Comprehensive Analytics Endpoint

**All analytics data in ONE API call - No need for multiple endpoints!**

### Why One Endpoint?
- ✅ **Faster**: Single request instead of 6+ separate calls
- ✅ **Simpler**: One API to integrate in frontend
- ✅ **Efficient**: Optimized database queries
- ✅ **Consistent**: All data from same point in time

### Endpoint
```
GET /api/v1/admin/analytics/comprehensive
```

### Authentication
Requires Admin or Super Admin role with Bearer token.

### What It Returns
All analytics data including:
1. **Stats** - Top metrics with trends (users, projects, revenue, page views)
2. **Growth Metrics** - 12 months of cumulative growth
3. **Demographics** - User distribution by role
4. **City Analytics** - Top 7 cities by project count
5. **Conversion Funnel** - 5-stage conversion tracking
6. **Landmark Performance** - Top 5 performing landmarks

---

## Response Structure

```json
{
  "stats": {
    "total_users": {
      "value": 1500,
      "change_percentage": 12.5,
      "trend": "up"
    },
    "active_projects": {
      "value": 240,
      "change_percentage": 8.3,
      "trend": "up"
    },
    "revenue": {
      "value": 1250000,
      "change_percentage": 15.2,
      "trend": "up"
    },
    "page_views": {
      "value": 45200,
      "change_percentage": -2.1,
      "trend": "down"
    }
  },
  "growth_metrics": [
    {
      "month": "Jan",
      "users": 120,
      "developers": 15,
      "projects": 25
    },
    {
      "month": "Feb",
      "users": 180,
      "developers": 22,
      "projects": 38
    }
    // ... 12 months total
  ],
  "demographics": [
    {
      "name": "Buyers",
      "value": 65
    },
    {
      "name": "Developers",
      "value": 20
    },
    {
      "name": "Agents",
      "value": 10
    },
    {
      "name": "Others",
      "value": 5
    }
  ],
  "city_analytics": [
    {
      "city": "Bangalore",
      "projects": 85,
      "users": 450
    },
    {
      "city": "Mumbai",
      "projects": 72,
      "users": 380
    }
    // ... top 7 cities
  ],
  "conversion_funnel": [
    {
      "name": "Website Visits",
      "value": 10000
    },
    {
      "name": "Property Views",
      "value": 6500
    },
    {
      "name": "Lead Submissions",
      "value": 2800
    },
    {
      "name": "Site Visits Booked",
      "value": 1200
    },
    {
      "name": "Conversions",
      "value": 350
    }
  ],
  "landmark_performance": [
    {
      "name": "Tech Parks",
      "views": 4500,
      "leads": 320
    },
    {
      "name": "Metro Stations",
      "views": 3800,
      "leads": 280
    }
    // ... top 5 landmarks
  ]
}
```

---

## Field Descriptions

### Stats
Top-level metrics with trend analysis (compared to last 30 days):

- **total_users**: Total buyer accounts
  - `value`: Current count
  - `change_percentage`: % change from last month
  - `trend`: "up" or "down"

- **active_projects**: Approved/active projects
  - Same structure as above

- **revenue**: Total revenue from active subscriptions
  - Value in currency units
  - Same trend structure

- **page_views**: Total project leads (proxy for page views)
  - Same trend structure

### Growth Metrics
Monthly cumulative data for the last 12 months:
- `month`: Month abbreviation (Jan, Feb, etc.)
- `users`: Cumulative buyer count up to that month
- `developers`: Cumulative developer count
- `projects`: Cumulative project count

### Demographics
User distribution by role (as percentages):
- `name`: Role name (Buyers, Developers, Agents, Others)
- `value`: Percentage of total users

### City Analytics
Top 7 cities by project count:
- `city`: City name
- `projects`: Number of projects in the city
- `users`: Number of buyers in the city

### Conversion Funnel
5-stage conversion funnel:
1. **Website Visits**: Estimated total visits
2. **Property Views**: Project leads created
3. **Lead Submissions**: Contacted/purchased leads
4. **Site Visits Booked**: Actual site visit bookings
5. **Conversions**: Completed purchases

### Landmark Performance
Top 5 performing landmarks:
- `name`: Landmark name
- `views`: Estimated views (based on projects)
- `leads`: Estimated leads (based on active layouts)

---

## Usage Examples

### JavaScript/TypeScript

```typescript
const fetchAnalytics = async () => {
  const response = await fetch('/api/v1/admin/analytics/comprehensive', {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  const analytics = await response.json();
  
  // Use stats for dashboard cards
  const { stats } = analytics;
  console.log(`Total Users: ${stats.total_users.value} (${stats.total_users.trend})`);
  console.log(`Revenue: ₹${stats.revenue.value}`);
  
  // Use growth_metrics for line chart
  const chartData = analytics.growth_metrics;
  
  // Use demographics for pie chart
  const pieData = analytics.demographics;
  
  // Use city_analytics for bar chart
  const cityData = analytics.city_analytics;
  
  // Use conversion_funnel for funnel chart
  const funnelData = analytics.conversion_funnel;
  
  return analytics;
};
```

### Python

```python
import requests

def get_analytics(token):
    response = requests.get(
        'http://localhost:8000/api/v1/admin/analytics/comprehensive',
        headers={'Authorization': f'Bearer {token}'}
    )
    analytics = response.json()
    
    # Access different sections
    stats = analytics['stats']
    growth = analytics['growth_metrics']
    demographics = analytics['demographics']
    cities = analytics['city_analytics']
    funnel = analytics['conversion_funnel']
    landmarks = analytics['landmark_performance']
    
    return analytics
```

---

## Frontend Integration

### Dashboard Stats Cards

```jsx
function StatsCards({ stats }) {
  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard
        title="Total Users"
        value={stats.total_users.value.toLocaleString()}
        change={stats.total_users.change_percentage}
        trend={stats.total_users.trend}
      />
      <StatCard
        title="Active Projects"
        value={stats.active_projects.value}
        change={stats.active_projects.change_percentage}
        trend={stats.active_projects.trend}
      />
      <StatCard
        title="Revenue"
        value={`₹${(stats.revenue.value / 100000).toFixed(1)}L`}
        change={stats.revenue.change_percentage}
        trend={stats.revenue.trend}
      />
      <StatCard
        title="Page Views"
        value={stats.page_views.value.toLocaleString()}
        change={stats.page_views.change_percentage}
        trend={stats.page_views.trend}
      />
    </div>
  );
}

function StatCard({ title, value, change, trend }) {
  const isPositive = trend === 'up';
  const color = isPositive ? 'text-green-600' : 'text-red-600';
  const icon = isPositive ? '↑' : '↓';
  
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-gray-500 text-sm">{title}</h3>
      <p className="text-3xl font-bold mt-2">{value}</p>
      <p className={`text-sm mt-2 ${color}`}>
        {icon} {Math.abs(change)}%
      </p>
    </div>
  );
}
```

### Growth Chart (Line Chart)

```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function GrowthChart({ data }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-bold mb-4">Growth Metrics</h3>
      <LineChart width={800} height={400} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="users" stroke="#8884d8" name="Users" />
        <Line type="monotone" dataKey="developers" stroke="#82ca9d" name="Developers" />
        <Line type="monotone" dataKey="projects" stroke="#ffc658" name="Projects" />
      </LineChart>
    </div>
  );
}
```

### Demographics Pie Chart

```jsx
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

function DemographicsChart({ data }) {
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
  
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-bold mb-4">User Demographics</h3>
      <PieChart width={400} height={400}>
        <Pie
          data={data}
          cx={200}
          cy={200}
          labelLine={false}
          label={({ name, value }) => `${name}: ${value}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </div>
  );
}
```

### City Analytics Bar Chart

```jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function CityAnalytics({ data }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-bold mb-4">City Analytics</h3>
      <BarChart width={600} height={400} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="city" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="projects" fill="#8884d8" name="Projects" />
        <Bar dataKey="users" fill="#82ca9d" name="Users" />
      </BarChart>
    </div>
  );
}
```

### Conversion Funnel

```jsx
function ConversionFunnel({ data }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-bold mb-4">Conversion Funnel</h3>
      <div className="space-y-2">
        {data.map((stage, index) => {
          const percentage = index === 0 ? 100 : (stage.value / data[0].value * 100);
          return (
            <div key={stage.name} className="relative">
              <div className="flex justify-between mb-1">
                <span>{stage.name}</span>
                <span className="font-bold">{stage.value.toLocaleString()}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-8">
                <div
                  className="bg-blue-600 h-8 rounded-full flex items-center justify-end pr-2"
                  style={{ width: `${percentage}%` }}
                >
                  <span className="text-white text-sm">{percentage.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

### Landmark Performance

```jsx
function LandmarkPerformance({ data }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-bold mb-4">Top Performing Landmarks</h3>
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="text-left py-2">Landmark</th>
            <th className="text-right py-2">Views</th>
            <th className="text-right py-2">Leads</th>
          </tr>
        </thead>
        <tbody>
          {data.map((landmark, index) => (
            <tr key={index} className="border-b">
              <td className="py-2">{landmark.name}</td>
              <td className="text-right">{landmark.views.toLocaleString()}</td>
              <td className="text-right">{landmark.leads.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### Complete Analytics Page

```jsx
import { useState, useEffect } from 'react';

function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('/api/v1/admin/analytics/comprehensive', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!analytics) return <div>No data available</div>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
      
      {/* Stats Cards */}
      <StatsCards stats={analytics.stats} />
      
      {/* Charts Row 1 */}
      <div className="grid grid-cols-2 gap-6">
        <GrowthChart data={analytics.growth_metrics} />
        <DemographicsChart data={analytics.demographics} />
      </div>
      
      {/* Charts Row 2 */}
      <div className="grid grid-cols-2 gap-6">
        <CityAnalytics data={analytics.city_analytics} />
        <ConversionFunnel data={analytics.conversion_funnel} />
      </div>
      
      {/* Landmark Performance */}
      <LandmarkPerformance data={analytics.landmark_performance} />
    </div>
  );
}
```

---

## Notes

- **Single API Call**: All analytics data in one request for optimal performance
- **Real-time Data**: Calculated from actual database records
- **Trend Analysis**: Compares current values with 30 days ago
- **Growth Metrics**: Shows cumulative growth over 12 months
- **Top 7 Cities**: Sorted by project count
- **Top 5 Landmarks**: Sorted by active layouts

---

## Performance Considerations

- This endpoint makes multiple database queries
- Response time: ~2-5 seconds depending on data volume
- Consider caching for production (Redis with 5-minute TTL)
- Use loading states in frontend

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized"
}
```

---

**Ready to use!** 🚀

**Single endpoint for all analytics:** `http://localhost:8000/api/v1/admin/analytics/comprehensive`

No need for multiple API calls - everything you need in one response!
