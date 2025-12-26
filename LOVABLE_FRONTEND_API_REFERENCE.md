# Lovable Frontend - API Integration Guide

**Backend Base URL:** `https://notify.tattvasphere.com`

**API Version:** v1
**Generated:** 2025-12-26
**Status:** ✅ Production Ready

---

## 🔐 Authentication

All authenticated endpoints require a Bearer token in the Authorization header.

### Login Flow

```javascript
// 1. User Login
const response = await fetch('https://notify.tattvasphere.com/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
// Returns: { access_token: "eyJ...", token_type: "bearer", user: {...} }

// 2. Store token and use in subsequent requests
const token = data.access_token;

// 3. Make authenticated requests
const projects = await fetch('https://notify.tattvasphere.com/api/v1/users/me/wishlist', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## 📋 Table of Contents

1. [Authentication APIs](#authentication-apis)
2. [Public APIs (No Auth Required)](#public-apis)
3. [User Portal APIs](#user-portal-apis)
4. [Developer Portal APIs](#developer-portal-apis)
5. [Locality Intelligence APIs](#locality-intelligence-apis-map-integration)
6. [Admin Portal APIs](#admin-portal-apis)
7. [Lawyer Portal APIs](#lawyer-portal-apis)

---

## 1. Authentication APIs

**Base:** `https://notify.tattvasphere.com/api/v1/auth`

### Register New User
```http
POST /api/v1/auth/register
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe",
  "phone": "+91-9876543210"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "USER"
  }
}
```

---

### Login
```http
POST /api/v1/auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "USER",
    "profile": {
      "phone": "+91-9876543210"
    }
  }
}
```

---

## 2. Public APIs (No Auth Required)

### List Public Projects
```http
GET /api/v1/public/projects
```

**Query Parameters:**
- `city` (optional): Filter by city
- `skip` (default: 0): Pagination offset
- `limit` (default: 20): Number of results

**Example:**
```javascript
const projects = await fetch(
  'https://notify.tattvasphere.com/api/v1/public/projects?city=Bangalore&limit=10'
);
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Green Valley Residency",
    "slug": "green-valley-residency",
    "developer_id": "uuid",
    "description": "Luxury apartments in prime location",
    "address": {
      "street": "Hosur Road",
      "city": "Bangalore",
      "state": "Karnataka",
      "pincode": "560068",
      "country": "India"
    },
    "price_range": {
      "min": 5000000,
      "max": 15000000
    },
    "property_type": "apartment",
    "total_units": 200,
    "available_units": 45,
    "amenities": ["Swimming Pool", "Gym", "Clubhouse"],
    "images": ["https://notify.tattvasphere.com/uploads/..."],
    "latitude": 12.9141,
    "longitude": 77.6411,
    "status": "APPROVED",
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

---

### Get Project by Slug
```http
GET /api/v1/public/projects/{slug}
```

**Example:**
```javascript
const project = await fetch(
  'https://notify.tattvasphere.com/api/v1/public/projects/green-valley-residency'
);
```

---

### List Landmarks (Market Analyzer)
```http
GET /api/v1/public/landmarks
```

**Query Parameters:**
- `city` (optional): Filter by city

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Hosur Road",
    "city": "Bangalore",
    "latitude": 12.9141,
    "longitude": 77.6411,
    "avg_price_per_sqft": 8750,
    "median_price": 12500000
  }
]
```

---

### Get Landmark Details
```http
GET /api/v1/public/landmarks/{landmark_id}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Hosur Road",
  "city": "Bangalore",
  "zone": "South Bangalore",
  "latitude": 12.9141,
  "longitude": 77.6411,
  "avg_price_per_sqft": 8750,
  "median_price": 12500000,
  "growth_forecast_5yr": 63.6,
  "price_trend": "rising",
  "total_projects": 85,
  "description": "Mid-segment locality with excellent connectivity",
  "nearby_projects": [
    {
      "id": "uuid",
      "name": "Green Valley",
      "slug": "green-valley",
      "distance_km": 2.3
    }
  ]
}
```

---

## 3. User Portal APIs

**Authentication Required:** Yes (Bearer token)

### Get User Profile
```http
GET /api/v1/users/me
```

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+91-9876543210",
  "role": "USER"
}
```

---

### Update User Profile
```http
PATCH /api/v1/users/me
```

**Request:**
```json
{
  "full_name": "John Smith",
  "phone": "+91-9999999999"
}
```

---

### Get View History
```http
GET /api/v1/users/me/history
```

Returns list of projects the user has viewed.

---

### Get Wishlist
```http
GET /api/v1/users/me/wishlist
```

Returns list of wishlisted projects.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Green Valley Residency",
    "slug": "green-valley-residency",
    "price_range": {
      "min": 5000000,
      "max": 15000000
    },
    "images": ["https://notify.tattvasphere.com/uploads/..."]
  }
]
```

---

### User Interactions

#### Record Project View
```http
POST /api/v1/users/interactions/view
```

**Request:**
```json
{
  "project_id": "uuid"
}
```

---

#### Add to Wishlist
```http
POST /api/v1/users/interactions/wishlist
```

**Request:**
```json
{
  "project_id": "uuid"
}
```

---

#### Remove from Wishlist
```http
DELETE /api/v1/users/interactions/wishlist
```

**Request:**
```json
{
  "project_id": "uuid"
}
```

---

#### Request Legal Consultation
```http
POST /api/v1/users/interactions/legal-request
```

**Request:**
```json
{
  "project_id": "uuid",
  "preferred_time": "2025-12-30T14:00:00Z",
  "notes": "Need help with property verification"
}
```

---

#### Book Site Visit
```http
POST /api/v1/users/me/bookings
```

**Request:**
```json
{
  "project_id": "uuid",
  "scheduled_time": "2025-12-28T10:00:00Z",
  "pickup_location": "MG Road Metro Station",
  "visitor_name": "John Doe",
  "visitor_phone": "+91-9876543210"
}
```

**Response:**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "scheduled_time": "2025-12-28T10:00:00Z",
  "pickup_location": "MG Road Metro Station",
  "status": "PENDING",
  "created_at": "2025-12-26T10:30:00Z"
}
```

---

#### Get My Bookings
```http
GET /api/v1/users/me/bookings
```

---

## 4. Developer Portal APIs

**Authentication Required:** Yes (Developer/Manager/Admin role)

### Get Developer Dashboard
```http
GET /api/v1/developers/leads/dashboard
```

**Query Parameters:**
- `period` (optional): "day", "week", "month", "year"
- `start_date` (optional): ISO date
- `end_date` (optional): ISO date

**Response:**
```json
{
  "period_start": "2025-12-01T00:00:00Z",
  "period_end": "2025-12-26T23:59:59Z",
  "period_type": "month",
  "total_visitors": 1250,
  "total_plot_visits": 45,
  "total_legal_consultations": 23,
  "interested_visitors": 89,
  "total_views": 3420,
  "projects": [
    {
      "project_id": "uuid",
      "project_name": "Green Valley",
      "project_slug": "green-valley",
      "city": "Bangalore",
      "visitors": 450,
      "plot_visits": 15,
      "legal_consultations": 8,
      "interested_visitors": 32,
      "total_views": 1200
    }
  ]
}
```

---

### Get Analytics Dashboard
```http
GET /api/v1/developers/leads/analytics
```

**Response:**
```json
{
  "overview": {
    "total_views": 15000,
    "total_leads": 450,
    "wishlists": 120,
    "conversion_rate": 3.0
  },
  "weekly_performance": [
    {
      "week": "Week 1",
      "views": 3500,
      "leads": 105,
      "conversions": 12
    }
  ],
  "top_locations": [
    {
      "city": "Bangalore",
      "views": 8500,
      "leads": 255,
      "share": 56.7
    }
  ],
  "traffic_sources": [],
  "device_breakdown": {
    "mobile": 0.0,
    "desktop": 0.0,
    "tablet": 0.0
  }
}
```

---

### Manage Projects

#### List My Projects
```http
GET /api/v1/developers/projects
```

**Query Parameters:**
- `status` (optional): "DRAFT", "PENDING", "APPROVED", "REJECTED"

---

#### Create Project
```http
POST /api/v1/developers/projects
```

**Request:**
```json
{
  "name": "Sunset Villas",
  "description": "Premium villas with modern amenities",
  "address": {
    "street": "Sarjapur Road",
    "city": "Bangalore",
    "state": "Karnataka",
    "pincode": "560102",
    "country": "India"
  },
  "latitude": 12.9082,
  "longitude": 77.7606,
  "price_range": {
    "min": 8000000,
    "max": 25000000
  },
  "property_type": "villa",
  "total_units": 50,
  "available_units": 50,
  "amenities": ["Swimming Pool", "Garden", "Security"]
}
```

---

#### Update Project
```http
PUT /api/v1/developers/projects/{project_id}
```

---

#### Delete Project
```http
DELETE /api/v1/developers/projects/{project_id}
```

---

### Get Project Leads
```http
GET /api/v1/developers/leads/projects/{slug}/leads
```

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "project_id": "uuid",
    "is_wishlisted": true,
    "visit_status": "BOOKED",
    "legal_request_status": "PENDING",
    "first_viewed_at": "2025-12-20T10:30:00Z",
    "last_viewed_at": "2025-12-25T15:45:00Z",
    "view_count": 5
  }
]
```

---

### Upload Files
```http
POST /api/v1/developers/upload
```

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file`: File (PDF, JPG, PNG, HEIC, HEIF)
- `document_type`: "RERA_APPROVAL", "RTC", "DC_CONVERSION", "LAYOUT_APPROVAL", "PROJECT_IMAGE", "BROCHURE", "OTHER"

**Response:**
```json
{
  "file_url": "https://notify.tattvasphere.com/uploads/developer-123/RERA_APPROVAL/abc-123.pdf",
  "document_type": "RERA_APPROVAL"
}
```

---

## 5. Locality Intelligence APIs (Map Integration)

**Base:** `https://notify.tattvasphere.com/api/v1/locality`

### 🔥 Primary: Find Locality by Map Click
```http
GET /api/v1/locality/by-coordinates
```

**Query Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude
- `radius_km` (optional, default=5): Search radius

**Example:**
```javascript
// When user clicks map at Hosur Road, Bangalore
const response = await fetch(
  'https://notify.tattvasphere.com/api/v1/locality/by-coordinates?lat=12.9141&lng=77.6411'
);

const locality = await response.json();
console.log(locality.name); // "Hosur Road"
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Hosur Road",
  "city": "Bangalore",
  "zone": "South Bangalore",
  "rating": 4.3,
  "total_reviews": 5805,
  "avg_price_per_sqft": 8750,
  "growth_forecast_5yr": 63.6,
  "price_trend": "rising",
  "total_projects": 85,
  "description": "Mid-segment locality...",
  "latitude": 12.9141,
  "longitude": 77.6411
}
```

---

### Get Complete Locality Dashboard
```http
GET /api/v1/locality/{locality_id}/dashboard
```

**⭐ Best for: Loading complete 99acres-style page in one API call**

**Response:**
```json
{
  "overview": {
    "id": "uuid",
    "name": "Hosur Road",
    "city": "Bangalore",
    "rating": 4.3,
    "total_reviews": 5805,
    "avg_price_per_sqft": 8750
  },
  "price_insights": {
    "avg_price_sqft": 8750,
    "yoy_growth": 21.5,
    "last_5_year_growth": 63.6
  },
  "recent_transactions": [
    {
      "registry_date": "2025-09-29T00:00:00Z",
      "society_name": "Sattva Greenage",
      "agreement_price": 17800000,
      "area_sqft": 1345,
      "price_per_sqft": 13234,
      "bhk": 3,
      "floor": 6,
      "purchase_type": "Resale"
    }
  ],
  "price_trend": {
    "labels": ["2021", "2022", "2023", "2024", "2025"],
    "values": [5350, 6100, 7200, 8200, 8750],
    "transactions": [45, 52, 68, 72, 85]
  },
  "demand_overview": {
    "land": 36,
    "apartment": 35,
    "villa": 22,
    "independent_floor": 5
  },
  "supply_overview": {
    "apartment": 2900,
    "land": 998,
    "villa": 528,
    "independent_floor": 245
  },
  "top_societies": [
    {
      "id": "uuid",
      "name": "Sattva Greenage",
      "builder_name": "Sattva Group",
      "rating": 4.3,
      "total_reviews": 450,
      "price_range_min": 20500000,
      "price_range_max": 70000000
    }
  ],
  "rating_summary": {
    "overall": 4.3,
    "connectivity": 4.4,
    "lifestyle": 4.4,
    "safety": 4.1,
    "greenery": 4.1,
    "environment": 4.2,
    "total_reviews": 5805
  },
  "nearby_areas": [
    {
      "name": "Electronic City Phase 1",
      "distance_km": 4.5,
      "price_sqft": 7550,
      "price_difference_percent": -13.7
    }
  ]
}
```

---

### Other Locality Endpoints

#### Get Locality Overview
```http
GET /api/v1/locality/{locality_id}
```

#### Get Highlights
```http
GET /api/v1/locality/{locality_id}/highlights
```

#### Get Recent Transactions
```http
GET /api/v1/locality/{locality_id}/transactions?limit=20
```

#### Get Transaction Stats
```http
GET /api/v1/locality/{locality_id}/transactions/stats?months=12
```

#### Get Price Insights
```http
GET /api/v1/locality/{locality_id}/price-insights/summary
```

#### Get Price by BHK
```http
GET /api/v1/locality/{locality_id}/price-insights/by-bhk
```

#### Get Price Trend Graph
```http
GET /api/v1/locality/{locality_id}/trends/price?duration=5y
```

#### Compare with Nearby
```http
GET /api/v1/locality/{locality_id}/trends/compare
```

#### Get Demand Overview
```http
GET /api/v1/locality/{locality_id}/demand/overview
```

#### Get Societies
```http
GET /api/v1/locality/{locality_id}/societies?limit=10
```

#### Get Reviews
```http
GET /api/v1/locality/{locality_id}/reviews?limit=20
```

#### Get Ratings Summary
```http
GET /api/v1/locality/{locality_id}/reviews/ratings-summary
```

#### Get Nearby Areas
```http
GET /api/v1/locality/{locality_id}/nearby-areas?radius_km=10
```

---

## 6. Admin Portal APIs

**Authentication Required:** Yes (Admin/Super Admin role)

### Dashboard
```http
GET /api/v1/admin/dashboard
```

### Analytics
```http
GET /api/v1/admin/analytics/{endpoint}
```

### Manage Users
```http
GET /api/v1/admin/users
POST /api/v1/admin/users
GET /api/v1/admin/users/{user_id}
PUT /api/v1/admin/users/{user_id}
DELETE /api/v1/admin/users/{user_id}
PATCH /api/v1/admin/users/{user_id}/suspend
PATCH /api/v1/admin/users/{user_id}/activate
```

### Manage Developers
```http
GET /api/v1/admin/developers
POST /api/v1/admin/developers
GET /api/v1/admin/developers/{developer_id}
PUT /api/v1/admin/developers/{developer_id}
DELETE /api/v1/admin/developers/{developer_id}
```

### Manage Projects
```http
GET /api/v1/admin/projects
PATCH /api/v1/admin/projects/{project_id}/approve
PATCH /api/v1/admin/projects/{project_id}/reject
```

### Manage Landmarks
```http
GET /api/v1/admin/landmarks
POST /api/v1/admin/landmarks
PUT /api/v1/admin/landmarks/{landmark_id}
DELETE /api/v1/admin/landmarks/{landmark_id}
```

---

## 7. Lawyer Portal APIs

**Authentication Required:** Yes (Lawyer role)

### Get Dashboard Analytics
```http
GET /api/v1/lawyer/dashboard/analytics
```

### Manage Leads
```http
GET /api/v1/lawyer/leads
POST /api/v1/lawyer/leads
PATCH /api/v1/lawyer/leads/{lead_id}/status
```

### Get WhatsApp Link
```http
GET /api/v1/lawyer/leads/{lead_id}/whatsapp-link
```

### Manage Profile
```http
GET /api/v1/lawyer/profile
PATCH /api/v1/lawyer/profile
```

### Review Documents
```http
GET /api/v1/lawyer/projects/{project_id}/documents
PATCH /api/v1/lawyer/projects/{project_id}/documents/{doc_id}
```

### Manage Legal Calls
```http
GET /api/v1/lawyer/legal-calls
PATCH /api/v1/lawyer/legal-calls/{request_id}/complete
```

---

## 🔧 Error Responses

All API errors follow this format:

```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

---

## 📱 Frontend Integration Examples

### React/Next.js Example

```javascript
// lib/api.js
const API_BASE = 'https://notify.tattvasphere.com';

export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  if (!response.ok) throw new Error('Login failed');
  return response.json();
}

export async function getPublicProjects(city = null) {
  const url = new URL(`${API_BASE}/api/v1/public/projects`);
  if (city) url.searchParams.set('city', city);

  const response = await fetch(url);
  return response.json();
}

export async function getLocalityByCoordinates(lat, lng) {
  const response = await fetch(
    `${API_BASE}/api/v1/locality/by-coordinates?lat=${lat}&lng=${lng}`
  );
  return response.json();
}

export async function getLocalityDashboard(localityId) {
  const response = await fetch(
    `${API_BASE}/api/v1/locality/${localityId}/dashboard`
  );
  return response.json();
}

export async function addToWishlist(projectId, token) {
  const response = await fetch(
    `${API_BASE}/api/v1/users/interactions/wishlist`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ project_id: projectId })
    }
  );
  return response.json();
}
```

### Usage in Components

```javascript
// components/ProjectList.jsx
import { useEffect, useState } from 'react';
import { getPublicProjects } from '../lib/api';

export default function ProjectList({ city }) {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    getPublicProjects(city).then(setProjects);
  }, [city]);

  return (
    <div>
      {projects.map(project => (
        <div key={project.id}>
          <h2>{project.name}</h2>
          <p>{project.description}</p>
          <p>Price: ₹{project.price_range.min} - ₹{project.price_range.max}</p>
        </div>
      ))}
    </div>
  );
}
```

```javascript
// components/LocalityMap.jsx
import { useState } from 'react';
import { getLocalityByCoordinates, getLocalityDashboard } from '../lib/api';

export default function LocalityMap() {
  const [selectedLocality, setSelectedLocality] = useState(null);

  const handleMapClick = async (lat, lng) => {
    // Find locality
    const locality = await getLocalityByCoordinates(lat, lng);

    // Load full dashboard
    const dashboard = await getLocalityDashboard(locality.id);
    setSelectedLocality(dashboard);
  };

  return (
    <div>
      <MapComponent onClick={handleMapClick} />
      {selectedLocality && (
        <LocalityPanel data={selectedLocality} />
      )}
    </div>
  );
}
```

---

## 🌐 CORS Configuration

The API supports CORS for the following origins (update as needed):
- `http://localhost:3000` (development)
- `http://localhost:5173` (Vite development)
- Your production domain

---

## 📊 Rate Limiting

Current rate limits:
- Public endpoints: 60 requests/minute
- Authenticated endpoints: 120 requests/minute

---

## 🔗 Useful Links

- **Swagger UI (API Docs):** `https://notify.tattvasphere.com/docs`
- **Health Check:** `https://notify.tattvasphere.com/health`
- **Backend Repository:** [GitHub Link]
- **Support:** Contact backend team

---

**Last Updated:** 2025-12-26
**API Version:** v1
**Status:** ✅ Production Ready
