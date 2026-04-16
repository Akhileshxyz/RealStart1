# Landmark Admin Form - Frontend Documentation

## Overview
Landmark represents a locality/area in a city with market intelligence data, price history, and growth predictions.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/landmarks/` | List all landmarks |
| GET | `/api/v1/admin/landmarks/{id}` | Get single landmark |
| POST | `/api/v1/admin/landmarks/` | Create landmark |
| PUT | `/api/v1/admin/landmarks/{id}` | Update landmark |
| DELETE | `/api/v1/admin/landmarks/{id}` | Delete landmark |

---

## Form Fields

### Basic Information

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Landmark name (e.g., "Doddaballapura Bus Stand") |
| `city_id` | UUID | Yes | Reference to parent city |
| `hero_desc` | string | No | Short headline description |
| `description` | string | No | Full description of the area |
| `zone` | string | No | Zone name (e.g., "North Bengaluru", "East Bengaluru") |

### Location

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `latitude` | number | No | GPS latitude |
| `longitude` | number | No | GPS longitude |
| `location` | GeoJSON | No | GeoJSON Point format `{"type": "Point", "coordinates": [lng, lat]}` |

### Media

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `images` | string[] | No | Array of image URLs |

---

## Price Fields (Market Intelligence)

All price fields accept string format with units (no conversion done):

| Field | Type | Example Input | Description |
|-------|------|---------------|-------------|
| `avg_plot_price` | string | `"60 L"` or `"1.5 Cr"` | Average residential plot price |
| `avg_apartment_price` | string | `"80 L"` | Average apartment price |
| `avg_price_per_sqft` | string | `"5500"` | Price per square feet |
| `residential_rent_2bhk` | string | `"₹20,000"` | 2 BHK monthly rent |
| `rental_yield` | string | `"4.5%"` | Rental yield percentage |
| `price_trend` | string | `"rising"` | Price trend (rising/stable/falling) |
| `price_trend_3m` | string | `"+5.2%"` | 3-month price change |

---

## Price Growth (Last 5 Years)

Historical price data showing how prices have changed over the last 5 years.

### Data Structure
```json
{
  "price_growth": [
    {
      "year": 2020,
      "value": "20 L",
      "reason": "Market boom"
    },
    {
      "year": 2021,
      "value": "22 L",
      "reason": "Metro announced"
    },
    {
      "year": 2022,
      "value": "25 L",
      "reason": "IT hub expansion"
    },
    {
      "year": 2023,
      "value": "28 L",
      "reason": "Better connectivity"
    },
    {
      "year": 2024,
      "value": "32 L",
      "reason": "RERA compliance"
    }
  ]
}
```

### Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `year` | number | Yes | Year (e.g., 2020, 2021) |
| `value` | string | Yes | Price at that year (e.g., "20 L", "25 L") |
| `reason` | string | Yes | Reason for price change |

### Form UI Recommendation
```
┌─────────────────────────────────────────────────────┐
│  Price Growth (Last 5 Years)                        │
├─────────────────────────────────────────────────────┤
│  ┌──────┬──────────┬─────────────────────────┐     │
│  │ Year │ Price    │ Reason for Change       │     │
│  ├──────┼──────────┼─────────────────────────┤     │
│  │ 2020 │ [20 L  ] │ [Market boom          ] │ [+] │
│  │ 2021 │ [22 L  ] │ [Metro announced      ] │     │
│  │ 2022 │ [25 L  ] │ [IT hub expansion    ] │     │
│  │ 2023 │ [28 L  ] │ [Better connectivity ] │     │
│  │ 2024 │ [32 L  ] │ [RERA compliance     ] │     │
│  └──────┴──────────┴─────────────────────────┘     │
└─────────────────────────────────────────────────────┘
```

---

## Price Prediction (Next 5 Years)

Projected future prices and comparison with city average.

### Data Structure
```json
{
  "price_prediction": [
    {
      "year": 2025,
      "value": "35 L",
      "reason": "Projected metro impact"
    },
    {
      "year": 2026,
      "value": "38 L",
      "reason": "Infrastructure development"
    },
    {
      "year": 2027,
      "value": "42 L",
      "reason": "Growing demand"
    },
    {
      "year": 2028,
      "value": "46 L",
      "reason": "Established market"
    },
    {
      "year": 2029,
      "value": "50 L",
      "reason": "Full development"
    }
  ]
}
```

### Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `year` | number | Yes | Future year |
| `value` | string | Yes | Projected price |
| `reason` | string | Yes | Reason for prediction |

### Form UI Recommendation
```
┌────────────────────────────────────────────────────────────┐
│  Price Prediction (Next 5 Years)                           │
├────────────────────────────────────────────────────────────┤
│  ┌──────┬──────────────┬─────────────────────┐            │
│  │ Year │ Price (₹)    │ Reason              │            │
│  ├──────┼──────────────┼─────────────────────┤            │
│  │ 2025 │ [35 L      ] │ [Metro impact    ] │            │
│  │ 2026 │ [38 L      ] │ [Infrastructure ] │            │
│  │ 2027 │ [42 L      ] │ [Growing demand ] │            │
│  │ 2028 │ [46 L      ] │ [Established    ] │            │
│  │ 2029 │ [50 L      ] │ [Full dev       ] │            │
│  └──────┴──────────────┴─────────────────────┘            │
└────────────────────────────────────────────────────────────┘
```

---

## Upcoming Developments

List of upcoming infrastructure and development projects in the area. These are informational text items stored in Market Intelligence.

### Data Structure
```json
{
  "upcoming_projects": [
    {
      "title": "Namma Metro Phase 2",
      "detail": "New metro line connecting to central city"
    },
    {
      "title": "Shopping Mall Complex",
      "detail": "50,000 sqft retail space near bus stand"
    }
  ]
}
```

### Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Project name / Infrastructure name |
| `detail` | string | No | Brief description or impact |

### Form UI Recommendation
```
┌─────────────────────────────────────────────────────────────┐
│  Upcoming Developments                                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┬────────────────────────────────┐ │
│  │ Title                │ Detail                         │ │
│  ├──────────────────────┼────────────────────────────────┤ │
│  │ [Namma Metro Phase 2]│ [New metro line connecting...] │ │
│  │ [Shopping Mall      ]│ [50,000 sqft retail space...]  │ │
│  └──────────────────────┴────────────────────────────────┘ │
│  [+ Add Development]                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Statistics

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `total_projects` | number | No | Total projects count |
| `active_layouts_count` | number | No | Active layouts count |
| `rera_projects_count` | number | No | RERA approved projects |

---

## Risk Profile

| Field | Type | Options | Description |
|-------|------|---------|-------------|
| `risk_profile` | enum | `low`, `moderate`, `high` | Investment risk level |

---

## Relationships (IDs)

| Field | Type | Description |
|-------|------|-------------|
| `nearby_landmarks_ids` | UUID[] | IDs of nearby landmarks (manual) |
| `upcoming_project_ids` | UUID[] | Manual IDs for upcoming projects (Admin override) |
| `nearby_project_ids` | UUID[] | Manual IDs for nearby projects |

> [!NOTE] 
> **Automatic Linking**: Projects are automatically linked to a landmark if the project's `landmark_id` field matches this landmark. These will appear in the `upcoming_projects_list` response alongside the manual `upcoming_project_ids`.

---

## Example Create Request

```json
POST /api/v1/admin/landmarks/
{
  "name": "Doddaballapura Bus Stand",
  "city_id": "421e8329-a69c-4494-b640-5d09b78b6844",
  "hero_desc": "Central transport hub",
  "description": "The Near Doddaballapura Bus Stand area is the heartbeat of the town.",
  "zone": "North Bengaluru",
  "avg_plot_price": "60 L",
  "avg_apartment_price": "80 L",
  "residential_rent_2bhk": "₹20,000",
  "rental_yield": "4.5%",
  "price_trend": "rising",
  "price_trend_3m": "+5.2%",
  "price_growth": [
    {"year": 2020, "value": "20 L", "reason": "Market boom"},
    {"year": 2021, "value": "22 L", "reason": "Metro announced"},
    {"year": 2022, "value": "25 L", "reason": "IT hub expansion"},
    {"year": 2023, "value": "28 L", "reason": "Better connectivity"},
    {"year": 2024, "value": "32 L", "reason": "RERA compliance"}
  ],
  "price_prediction": [
    {"year": 2025, "value": "35 L", "reason": "Metro impact"},
    {"year": 2026, "value": "38 L", "reason": "Infrastructure"},
    {"year": 2027, "value": "42 L", "reason": "Growing demand"},
    {"year": 2028, "value": "46 L", "reason": "Established"},
    {"year": 2029, "value": "50 L", "reason": "Full development"}
  ],
  "risk_profile": "moderate",
  "total_projects": 15,
  "active_layouts_count": 8,
  "rera_projects_count": 5
}
```

---

## Notes for Frontend

1. **Price Values**: All price fields accept string format. Don't convert - send as entered (e.g., "60 L", "1.5 Cr")

2. **Dynamic Arrays**: price_growth and price_prediction are dynamic arrays - allow adding/removing rows

3. **Year Validation**: For price_growth, validate years are sequential and in the past
   For price_prediction, validate years are sequential and in the future

4. **Price Format**: Accept formats like:
   - `"20 L"` or `"20L"` (Lakhs)
   - `"1.5 Cr"` or `"1.5CR"` (Crores)
   - `"20,000"` (plain number)
   - `"₹20 L"` (with symbol)

5. **Images**: Images are uploaded separately via file upload endpoint.

6. **Auto-Approval**: When an admin creates or updates a project, the system automatically sets it to `APPROVED`. Manual approval via the Approval button is only required for projects submitted by developers.

7. **Project Visibility**: Public landmark pages show all projects linked to them regardless of approval status (if linked by admin or explicitly).
