# Admin Dashboard API Response Format

## Endpoint
```
GET /api/v1/admin/dashboard
```

## Authentication
Requires Admin or Super Admin role with Bearer token.

## Response Structure

```json
{
  "projects": {
    "total": 150,
    "active": 120,
    "pending_approval": 15
  },
  "users": {
    "total": 450,
    "developers": 75,
    "buyers": 375
  },
  "subscriptions": {
    "active_count": 65
  },
  "engagement": {
    "total_visits_booked": 1250
  },
  "action_items": {
    "pending_approvals": [
      {
        "project_id": "c7c32934-4ebb-47ee-96c9-d3a9cbc41559",
        "project_name": "Sunrise Apartments",
        "developer_name": "ABC Developers Ltd",
        "submitted_at": "2025-12-30T10:30:00Z"
      },
      {
        "project_id": "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6",
        "project_name": "Green Valley Residency",
        "developer_name": "XYZ Constructions",
        "submitted_at": "2025-12-29T15:45:00Z"
      }
    ],
    "total_pending_count": 15,
    "important_alerts": [
      {
        "title": "Subscription Expiring Soon",
        "message": "5 subscriptions expiring in next 7 days"
      },
      {
        "title": "High Pending Approvals",
        "message": "15 projects awaiting review"
      }
    ]
  }
}
```

## Field Descriptions

### Projects
- `total`: Total number of projects in the system
- `active`: Number of approved/active projects
- `pending_approval`: Number of projects waiting for admin approval

### Users
- `total`: Total registered users
- `developers`: Number of developer accounts
- `buyers`: Number of buyer/end-user accounts

### Subscriptions
- `active_count`: Number of currently active subscriptions

### Engagement
- `total_visits_booked`: Total number of site visits booked

### Action Items

#### pending_approvals
Array of projects pending approval (limited to 5 most recent):
- `project_id`: Unique project identifier (UUID as string)
- `project_name`: Name of the project
- `developer_name`: Name of the developer who submitted
- `submitted_at`: ISO 8601 timestamp of submission

#### important_alerts
Array of important system alerts:
- `title`: Alert title/category
- `message`: Descriptive message with counts

**Alert Types:**
1. **Subscription Expiring Soon** - Shows when subscriptions are expiring within 7 days
2. **Pending Approvals** / **High Pending Approvals** - Shows pending project count
   - "High Pending Approvals" when count > 10
   - "Pending Approvals" when count ≤ 10

## Usage Example

### JavaScript/TypeScript
```typescript
const fetchDashboardStats = async () => {
  const response = await fetch('/api/v1/admin/dashboard', {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  const data = await response.json();
  
  // Access stats
  console.log(`Total Projects: ${data.projects.total}`);
  console.log(`Active Subscriptions: ${data.subscriptions.active_count}`);
  console.log(`Pending Approvals: ${data.action_items.total_pending_count}`);
  
  // Display alerts
  data.action_items.important_alerts.forEach(alert => {
    console.log(`${alert.title}: ${alert.message}`);
  });
  
  // Show pending projects
  data.action_items.pending_approvals.forEach(project => {
    console.log(`${project.project_name} by ${project.developer_name}`);
  });
};
```

### Python
```python
import requests

def get_dashboard_stats(token):
    response = requests.get(
        'http://localhost:8000/api/v1/admin/dashboard',
        headers={'Authorization': f'Bearer {token}'}
    )
    data = response.json()
    
    print(f"Total Projects: {data['projects']['total']}")
    print(f"Active Subscriptions: {data['subscriptions']['active_count']}")
    
    for alert in data['action_items']['important_alerts']:
        print(f"{alert['title']}: {alert['message']}")
    
    return data
```

## Frontend Integration

### Dashboard Cards
```jsx
function DashboardStats({ stats }) {
  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard 
        title="Total Projects" 
        value={stats.projects.total}
        subtitle={`${stats.projects.pending_approval} pending`}
      />
      <StatCard 
        title="Total Users" 
        value={stats.users.total}
        subtitle={`${stats.users.developers} developers`}
      />
      <StatCard 
        title="Active Subscriptions" 
        value={stats.subscriptions.active_count}
      />
      <StatCard 
        title="Site Visits" 
        value={stats.engagement.total_visits_booked}
      />
    </div>
  );
}
```

### Alerts Section
```jsx
function AlertsSection({ alerts }) {
  return (
    <div className="alerts">
      {alerts.map((alert, index) => (
        <div key={index} className="alert">
          <h4>{alert.title}</h4>
          <p>{alert.message}</p>
        </div>
      ))}
    </div>
  );
}
```

### Pending Approvals Table
```jsx
function PendingApprovals({ approvals }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Project</th>
          <th>Developer</th>
          <th>Submitted</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {approvals.map(project => (
          <tr key={project.project_id}>
            <td>{project.project_name}</td>
            <td>{project.developer_name}</td>
            <td>{new Date(project.submitted_at).toLocaleDateString()}</td>
            <td>
              <button onClick={() => handleApprove(project.project_id)}>
                Approve
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## Notes

- The `pending_approvals` array is limited to the 5 most recent submissions
- Use `total_pending_count` to show the full count
- Alerts are dynamically generated based on system state
- All timestamps are in ISO 8601 format (UTC)
- UUIDs are returned as strings for JSON compatibility

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

## Related Endpoints

- `GET /api/v1/admin/system-health` - System health check
- `GET /api/v1/admin/projects/` - Full projects list
- `GET /api/v1/admin/subscriptions/stats` - Detailed subscription stats
