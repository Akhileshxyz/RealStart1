# Lovable UI Generation Prompts

**Project:** Realstart - Real Estate Platform
**Backend API:** `https://notify.tattvasphere.com`
**Generated:** 2025-12-26

Use these prompts in Lovable to generate the complete UI for your real estate platform.

---

## 🎨 Design System Prompt

```
Create a modern design system for a real estate platform called "Realstart" with the following specifications:

Colors:
- Primary: #2563eb (Blue)
- Secondary: #059669 (Green)
- Accent: #f59e0b (Amber)
- Background: #f9fafb (Light gray)
- Text: #1f2937 (Dark gray)
- Error: #dc2626 (Red)
- Success: #10b981 (Green)

Typography:
- Font family: Inter, system-ui, sans-serif
- Headings: font-weight 700
- Body: font-weight 400
- Use Tailwind CSS classes

Components style:
- Rounded corners (rounded-lg)
- Subtle shadows (shadow-md)
- Smooth transitions
- Modern card-based layouts
- Responsive mobile-first design

Include:
- Navigation bar with logo, menu items, and user profile
- Footer with links and contact info
- Button components (primary, secondary, outline)
- Form inputs with validation states
- Card components for projects and localities
- Modal/Dialog components
- Loading states and skeletons
- Toast notifications for success/error messages
```

---

## 📱 Page Generation Prompts

### 1. Homepage

```
Create a modern homepage for Realstart real estate platform with:

Header:
- Sticky navigation bar with logo "Realstart"
- Menu items: Home, Properties, Localities, About, Contact
- Right side: Login and Sign Up buttons
- Mobile hamburger menu

Hero Section:
- Large heading: "Find Your Dream Property in India"
- Subheading: "Discover premium properties with verified legal documents"
- Search bar with:
  - City dropdown (Bangalore, Hyderabad, Mumbai, Delhi)
  - Property type dropdown (Apartment, Villa, Plot, Independent Floor)
  - Price range slider
  - "Search Properties" button
- Background: gradient overlay on real estate image

Features Section:
- 4 feature cards in a grid:
  1. "Verified Properties" - icon and description
  2. "Legal Assistance" - icon and description
  3. "Site Visit Booking" - icon and description
  4. "Market Analytics" - icon and description

Featured Properties:
- Horizontal scrollable carousel
- Show 3 property cards with:
  - Image
  - Property name
  - Location
  - Price range
  - BHK config
  - "View Details" button
  - Heart icon for wishlist

Statistics Section:
- 4 stat cards showing:
  - 10,000+ Properties
  - 500+ Developers
  - 50+ Cities
  - 95% Customer Satisfaction

Call to Action:
- "Ready to find your perfect home?"
- "Get Started" button

Footer:
- 4 columns: About, Quick Links, Contact, Social Media
- Copyright text

API Integration:
- Fetch featured projects from: GET https://notify.tattvasphere.com/api/v1/public/projects?limit=6
- Use React hooks (useState, useEffect)
- Show loading skeleton while fetching
```

---

### 2. Property Listing Page

```
Create a property listing page for Realstart with:

Header:
- Same navigation as homepage
- Breadcrumb: Home > Properties

Filters Sidebar (left):
- City selector (multi-select)
- Price range slider (min: 0, max: 10 Cr)
- Property type checkboxes
- BHK configuration checkboxes (1, 2, 3, 4+)
- Amenities checkboxes (Pool, Gym, Garden, Security, etc.)
- "Apply Filters" button
- "Reset Filters" button

Main Content (right):
- Sorting dropdown: "Sort by: Newest, Price (Low to High), Price (High to Low)"
- Results count: "Showing 45 properties"
- Grid of property cards (3 columns on desktop, 1 on mobile):
  - Large image (with image carousel dots)
  - Wishlist heart icon (top right)
  - Property name and developer
  - Location with map pin icon
  - Price in INR with "onwards" text
  - Configuration: "3, 4 BHK | 1200-1800 sq.ft"
  - Amenities icons (first 4)
  - "View Details" button
  - "Book Site Visit" button

Pagination:
- Page numbers and next/prev buttons at bottom

Mobile:
- Filters in slide-out drawer
- Filter button with badge showing active filter count

API Integration:
- GET https://notify.tattvasphere.com/api/v1/public/projects
- Query params: city, skip, limit
- Implement client-side filtering for better UX
- Use Intersection Observer for infinite scroll (optional)
```

---

### 3. Property Detail Page

```
Create a detailed property view page with:

Image Gallery:
- Large main image
- Thumbnail strip below (horizontal scroll)
- Fullscreen gallery modal on click
- Image navigation arrows

Property Header:
- Property name (large heading)
- Location with map pin icon
- Developer name with link
- Share button
- Wishlist button (filled if already wishlisted)

Quick Info Cards (grid):
- Price Range
- Property Type
- Total Units
- Available Units
- Possession Status
- RERA Registration

Tabs Section:
1. Overview Tab:
   - Full description
   - Key highlights (bullet points)
   - Amenities grid with icons

2. Floor Plans Tab:
   - BHK-wise floor plan images
   - Download button for each

3. Location Tab:
   - Embedded Mappls/Google Map
   - Nearby landmarks list:
     - Schools
     - Hospitals
     - Malls
     - Metro stations
   - Distance in km for each

4. Documents Tab:
   - List of uploaded documents:
     - RERA Approval
     - Layout Plan
     - Legal Documents
   - Download/View buttons
   - Verification badges

5. Reviews Tab (if implemented):
   - Overall rating stars
   - User reviews list
   - "Write a Review" button

Sticky CTA Bar (bottom on mobile):
- "Book Site Visit" button
- "Request Legal Help" button
- "Call Developer" button

Contact Form Card:
- "Interested in this property?"
- Name, Email, Phone inputs
- "I agree to terms" checkbox
- "Submit Inquiry" button

Similar Properties:
- Horizontal scrollable carousel
- 4-5 similar properties

API Integration:
- GET https://notify.tattvasphere.com/api/v1/public/projects/{slug}
- POST https://notify.tattvasphere.com/api/v1/users/interactions/view (with auth)
- POST https://notify.tattvasphere.com/api/v1/users/interactions/wishlist (with auth)
- POST https://notify.tattvasphere.com/api/v1/users/me/bookings (for site visit booking)
```

---

### 4. Map-Based Locality Page (99acres style)

```
Create a locality intelligence page triggered by map clicks:

Top Section:
- Back button
- Locality name heading: "Hosur Road, Bangalore"
- Overall rating: 4.3 stars (5805 reviews)
- Location badge: "South Bangalore"

Quick Stats Cards (grid of 4):
- Avg Price/sqft: "₹8,750"
- YoY Growth: "↑ 21.5%"
- Total Projects: "85"
- Total Transactions: "1,250"

Price Insights Section:
- Card with heading "Price Trends"
- Line chart showing 5-year price history
- X-axis: Years (2021-2025)
- Y-axis: Price per sqft
- Tooltip on hover
- Toggle buttons: 1Y, 3Y, 5Y, 10Y

Price by BHK Section:
- Card with heading "Price Range by Configuration"
- 4 rows for 1BHK, 2BHK, 3BHK, 4BHK
- Show min-max range for each
- Bar chart visualization

Recent Transactions Table:
- Heading: "Recent Registry Transactions"
- Scrollable table with columns:
  - Date
  - Society Name
  - Price
  - Area (sqft)
  - Price/sqft
  - BHK
  - Floor
  - Type (Resale/New)
- Show 10 rows, "View All" button

Demand & Supply:
- Two pie charts side by side
- Demand by Property Type
- Supply by Property Type

Top Societies:
- Card carousel
- Each card shows:
  - Society name
  - Builder name
  - Rating
  - Price range
  - Units count
  - Amenities icons
  - "View Details" button

Reviews Section:
- Overall ratings breakdown:
  - Connectivity: 4.4/5
  - Lifestyle: 4.4/5
  - Safety: 4.1/5
  - Greenery: 4.1/5
  - Environment: 4.2/5
- Recent reviews list (5 reviews)
- Star rating, user name, date, review text
- "Read All Reviews" button

Nearby Areas Comparison:
- Table comparing nearby localities
- Columns: Name, Distance (km), Avg Price, Price Difference %
- Color code: green for cheaper, red for expensive

API Integration:
- GET https://notify.tattvasphere.com/api/v1/locality/{locality_id}/dashboard
- This single API returns ALL data needed
- Use Chart.js or Recharts for visualizations
- Implement skeleton loaders
```

---

### 5. Interactive Map Page

```
Create an interactive map page for exploring localities:

Full-Screen Map:
- Integrate Mappls Maps SDK
- API key from env: MAPPLS_API_KEY
- Default center: Bangalore (12.9716, 77.5946)
- Zoom level: 12

Map Controls:
- Zoom in/out buttons
- Current location button
- City selector dropdown (floating top-left)
- Search bar for location search (floating top)

Map Markers:
- Show markers for all landmarks
- Custom marker icon (house icon)
- Different colors based on price range:
  - Green: Budget (<50L)
  - Blue: Mid-range (50L-1Cr)
  - Orange: Premium (1Cr-2Cr)
  - Red: Luxury (>2Cr)

Marker Click Behavior:
- Show info popup with:
  - Locality name
  - Avg price/sqft
  - Total projects
  - "View Details" button

Locality Panel (right sidebar):
- Slides in when marker clicked
- Shows locality overview
- Quick stats
- "View Full Dashboard" button that navigates to locality detail page

Filter Panel (left sidebar):
- Toggle to show/hide markers by price range
- Property type filter
- "Apply" button

API Integration:
- On map click at coordinates (lat, lng):
  GET https://notify.tattvasphere.com/api/v1/locality/by-coordinates?lat={lat}&lng={lng}
- Show locality info in panel
- On "View Details" -> Navigate to locality dashboard page

JavaScript Example:
```javascript
map.on('click', async (e) => {
  const { lat, lng } = e.latlng;
  const response = await fetch(
    `https://notify.tattvasphere.com/api/v1/locality/by-coordinates?lat=${lat}&lng=${lng}`
  );
  const locality = await response.json();
  showLocalityPanel(locality);
});
```
```

---

### 6. User Authentication Pages

```
Create login and registration pages:

LOGIN PAGE:
- Centered card layout
- Logo and "Welcome Back" heading
- Email input (with validation)
- Password input (with show/hide toggle)
- "Remember me" checkbox
- "Login" button (full width, primary color)
- "Forgot password?" link
- Divider with "or"
- "Sign up" link: "Don't have an account? Sign up"
- Background: subtle gradient

API Integration:
POST https://notify.tattvasphere.com/api/v1/auth/login
Body: { email, password }
Response: { access_token, user }
Store token in localStorage
Redirect to dashboard after login

REGISTRATION PAGE:
- Similar layout to login
- "Create Account" heading
- Form fields:
  - Full Name
  - Email
  - Phone (with +91 prefix)
  - Password (with strength indicator)
  - Confirm Password
  - Terms & Conditions checkbox
- "Sign Up" button
- "Already have an account? Login" link

API Integration:
POST https://notify.tattvasphere.com/api/v1/auth/register
Body: { email, password, full_name, phone }

Validation:
- Email format validation
- Password min 8 characters
- Phone 10 digits
- Show error messages below fields
- Disable submit until all valid
```

---

### 7. User Dashboard

```
Create a user dashboard page with:

Sidebar Navigation:
- Profile (icon + name)
- Dashboard (active)
- My Wishlist
- View History
- Site Visits
- Legal Requests
- Settings
- Logout

Dashboard Content:
Header:
- "Welcome back, John!" greeting
- Current date

Quick Stats Cards (grid of 4):
- Wishlisted Properties (count)
- Scheduled Visits (count)
- Legal Requests (count)
- Properties Viewed (count)

Recent Activity Timeline:
- List of recent actions
- Icons for each action type
- Timestamp
- Project name with link

Wishlisted Properties:
- Grid of property cards (2 columns)
- Same design as listing page
- "Remove from Wishlist" button
- "Schedule Visit" button
- Empty state: "No properties in wishlist"

Upcoming Site Visits:
- List of scheduled visits
- Show: Date, Time, Property, Pickup Location, Status
- "Reschedule" and "Cancel" buttons
- Empty state message

Recommended Properties:
- "Based on your interests"
- Horizontal scrollable carousel
- Property cards

API Integration:
- GET https://notify.tattvasphere.com/api/v1/users/me (profile)
- GET https://notify.tattvasphere.com/api/v1/users/me/wishlist
- GET https://notify.tattvasphere.com/api/v1/users/me/history
- GET https://notify.tattvasphere.com/api/v1/users/me/bookings
- Requires Authorization header with Bearer token
```

---

### 8. Developer Dashboard

```
Create a developer portal dashboard with:

Top Bar:
- Developer name and company logo
- Notification bell icon (with badge)
- Profile dropdown

Overview Cards (grid of 6):
- Total Visitors (big number + trend arrow)
- Plot Visit Bookings (count)
- Legal Consultations (count)
- Interested Buyers (count)
- Total Projects (count)
- Active Listings (count)

Charts Section:
- Visitors & Leads Trend (line chart)
- X-axis: Last 7 days/weeks/months
- Y-axis: Count
- Toggle: Day, Week, Month, Year

Leads by Project:
- Table with columns:
  - Project Name
  - Visitors
  - Wishlists
  - Visit Bookings
  - Legal Requests
  - Conversion Rate
- Sortable columns
- Pagination

Recent Activity Feed:
- Real-time feed of user actions:
  - "User X viewed Green Valley"
  - "User Y added Sunset Villas to wishlist"
  - "User Z booked site visit"
- Timestamp for each
- Auto-refresh every 30 seconds

Projects Management:
- List of developer's projects
- Each row:
  - Project thumbnail
  - Name, location, status
  - Quick stats (views, leads)
  - Action buttons: Edit, View, Delete
- "Add New Project" button

API Integration:
- GET https://notify.tattvasphere.com/api/v1/developers/leads/dashboard
- GET https://notify.tattvasphere.com/api/v1/developers/leads/analytics
- GET https://notify.tattvasphere.com/api/v1/developers/projects
- Requires Authorization with DEVELOPER/MANAGER/ADMIN role
```

---

### 9. Site Visit Booking Modal

```
Create a modal/dialog for booking site visits:

Header:
- "Book Site Visit" title
- Close button (X)

Property Info (read-only):
- Property name
- Location
- Small thumbnail image

Form:
- Date Picker:
  - Label: "Preferred Date"
  - Disable past dates
  - Highlight available dates

- Time Picker:
  - Label: "Preferred Time"
  - Options: 10 AM, 11 AM, 2 PM, 3 PM, 4 PM

- Pickup Location:
  - Text input or dropdown
  - Placeholder: "Enter pickup location"
  - Optional: Integration with maps autocomplete

- Visitor Name:
  - Pre-filled from user profile
  - Editable

- Phone Number:
  - Pre-filled from user profile
  - Format: +91-XXXXXXXXXX

- Special Requests (optional):
  - Textarea
  - Placeholder: "Any specific requirements?"

Buttons:
- "Cancel" (secondary)
- "Confirm Booking" (primary)

Success State:
- Replace form with success message
- "Booking Confirmed!" heading
- Booking details summary
- "Add to Calendar" button
- "Close" button

API Integration:
POST https://notify.tattvasphere.com/api/v1/users/me/bookings
Body: {
  project_id: "uuid",
  scheduled_time: "2025-12-28T10:00:00Z",
  pickup_location: "MG Road Metro",
  visitor_name: "John Doe",
  visitor_phone: "+91-9876543210"
}
```

---

### 10. Admin Portal

```
Create an admin dashboard with:

Sidebar:
- Dashboard
- Users
- Developers
- Projects
- Landmarks
- Analytics
- Ads Management
- Team
- Subscriptions
- Videos
- Settings

Dashboard Overview:
- System Health Cards:
  - Total Users
  - Total Developers
  - Total Projects
  - Total Transactions
  - Active Subscriptions
  - Revenue (This Month)

Quick Actions:
- Approve Pending Projects (badge with count)
- Review Legal Requests
- Manage Subscriptions
- View Analytics

Recent Activity:
- Timeline of recent system events
- User registrations
- Project submissions
- Subscription purchases

Charts:
- User Growth (line chart)
- Revenue by Month (bar chart)
- Properties by City (pie chart)

Pending Approvals Table:
- Project Name
- Developer
- Submitted Date
- Status
- Actions: Approve/Reject buttons

Alerts Section:
- Expiring Subscriptions (within 7 days)
- Flagged Content
- System Notifications

API Integration:
- GET https://notify.tattvasphere.com/api/v1/admin/dashboard
- GET https://notify.tattvasphere.com/api/v1/admin/projects?status=PENDING
- PATCH https://notify.tattvasphere.com/api/v1/admin/projects/{id}/approve
- Requires ADMIN or SUPER_ADMIN role
```

---

## 🎨 Reusable Components Prompts

### Property Card Component

```
Create a reusable PropertyCard React component:

Props:
- project: object with all project data
- showActions: boolean (default true)
- onWishlist: function
- onView: function

Card Structure:
- Image with aspect ratio 16:9
- Image carousel indicators (if multiple images)
- Wishlist heart button (top right, absolute position)
- Badge for "New" or "Featured" (top left)
- Content section:
  - Property name (truncate after 2 lines)
  - Developer name (smaller, muted text)
  - Location with pin icon
  - Price range (large, bold)
  - Configuration: "3, 4 BHK"
  - Amenities icons (first 3)
- Actions (if showActions):
  - "View Details" button
  - "Book Visit" button

Styles:
- Card with shadow on hover
- Smooth transitions
- Responsive: full width on mobile, fixed width on desktop

Example Usage:
<PropertyCard
  project={projectData}
  showActions={true}
  onWishlist={handleWishlist}
  onView={handleView}
/>
```

---

### Loading Skeleton Component

```
Create loading skeleton components for:

1. PropertyCardSkeleton:
- Gray rectangle for image (shimmer animation)
- 2 gray lines for text
- 1 gray line for price
- 2 gray buttons

2. PropertyDetailSkeleton:
- Large rectangle for hero image
- Text skeletons for heading
- Multiple paragraphs
- Grid of stat cards

3. DashboardSkeleton:
- Skeleton for stats cards
- Skeleton for charts
- Skeleton for tables

Use:
- Tailwind CSS
- Shimmer/pulse animation
- Match actual component dimensions
```

---

## 🔧 Utility Prompts

### API Client Setup

```
Create an API client utility file (lib/api.js):

Features:
- Base URL from environment variable or default to production
- Axios instance with interceptors
- Automatic token injection from localStorage
- Error handling with toast notifications
- Request/response logging in development
- Retry logic for failed requests
- Timeout configuration

Functions:
- login(email, password)
- register(userData)
- getPublicProjects(filters)
- getProjectBySlug(slug)
- addToWishlist(projectId)
- removeFromWishlist(projectId)
- bookSiteVisit(bookingData)
- getLocalityByCoordinates(lat, lng)
- getLocalityDashboard(localityId)
- All other API endpoints

Error Handling:
- 401: Redirect to login
- 403: Show permission error
- 500: Show generic error message
- Network error: Show retry option

Export as default object with all methods
```

---

### Authentication Context

```
Create a React Context for authentication:

Features:
- Store user data and token
- Login function
- Logout function
- Register function
- Auto-login on app load (check localStorage)
- Protected route wrapper
- Role-based access control

Usage:
const { user, token, login, logout, isAuthenticated } = useAuth();

if (isAuthenticated) {
  // Show authenticated content
}

Wrap app with:
<AuthProvider>
  <App />
</AuthProvider>
```

---

## 📦 Complete Project Setup Prompt

```
Create a complete Next.js/React project for Realstart with:

Tech Stack:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Axios for API calls
- Chart.js or Recharts for graphs
- React Hook Form for forms
- Zod for validation
- Lucide React for icons
- Sonner for toast notifications
- Date-fns for date formatting

Project Structure:
/app
  /(auth)
    /login
    /register
  /(main)
    /properties
    /property/[slug]
    /localities
    /locality/[id]
    /map
    /dashboard
  /(developer)
    /developer/dashboard
    /developer/projects
  /(admin)
    /admin/dashboard
    /admin/users

/components
  /ui (shadcn components)
  /property
  /locality
  /layout

/lib
  /api.ts (API client)
  /utils.ts
  /constants.ts

/hooks
  /useAuth.ts
  /useProjects.ts
  /useLocality.ts

Environment Variables:
NEXT_PUBLIC_API_URL=https://notify.tattvasphere.com
NEXT_PUBLIC_MAPPLS_API_KEY=rmblukatmrgrzgnhztulpbneakmpxtkinhmf

Install commands:
npm install axios react-hook-form zod @hookform/resolvers
npm install chart.js react-chartjs-2
npm install date-fns
npm install lucide-react
npm install sonner

Generate all pages mentioned above with proper routing, API integration, and state management.
```

---

## 🎯 Priority Order for Development

Use these prompts in this order:

1. **Design System** - Set up colors, typography, components
2. **API Client** - Create utility for API calls
3. **Authentication** - Login/Register pages and context
4. **Homepage** - Landing page with search
5. **Property Listing** - Browse properties
6. **Property Detail** - Individual property view
7. **User Dashboard** - User profile and actions
8. **Map & Locality** - Interactive map and locality intelligence
9. **Developer Dashboard** - Developer portal
10. **Admin Portal** - Admin management

---

**Tips for Lovable:**
- Use these prompts one at a time
- Start with the design system
- Each prompt is self-contained
- Mention API endpoints clearly
- Include error handling in prompts
- Request loading states
- Always ask for responsive design
- Include empty states

**Generated:** 2025-12-26
**Ready to use in Lovable!** 🚀
