

---

# **📌 Backend Developer Instruction**

### **Map-based Locality Page (99acres-like) using Mappls \+ FastAPI**

---

## **🎯 Goal (One-line)**

When a user selects a **location on Mappls map (by name or pin)**, backend should **resolve coordinates → locality\_id → load all locality APIs** and return **full locality details, prices, trends, graphs, demand, supply, societies, reviews, etc.**

---

## **🧭 High-Level Flow (IMPORTANT)**

Mappls Search / Map Click  
        ↓  
Coordinates (lat, lng)  
        ↓  
Backend: resolve locality  
        ↓  
Fetch locality\_id  
        ↓  
Load all locality APIs  
        ↓  
Frontend renders locality page

---

## **1️⃣ Step 1: Location Selection (Frontend → Backend)**

### **From Mappls**

Frontend will send either:

* `place_name` (e.g., "Hosur Road")  
* OR `latitude + longitude`

### **API call**

POST /api/v1/location/resolve

### **Request**

{  
  "place\_name": "Hosur Road",  
  "latitude": 12.8916,  
  "longitude": 77.6399  
}

---

## **2️⃣ Step 2: Resolve Coordinates → Locality (Backend Logic)**

### **Backend responsibility**

1. Use **Mappls Reverse Geocoding API**  
2. Identify:  
   * locality name  
   * city  
   * zone  
3. Match or create `locality_id` in DB

### **Pseudocode**

locality \= db.localities.find\_one({  
  "name": "Hosur Road",  
  "city": "Bangalore"  
})

if not locality:  
    locality\_id \= create\_locality\_from\_mappls()  
else:  
    locality\_id \= locality\["\_id"\]

---

## **3️⃣ Step 3: Canonical Locality API (MASTER API)**

This is the **single source of truth**.

GET /api/v1/locality/{locality\_id}

This API returns:

* locality name  
* city  
* rating  
* review count  
* about text  
* bounding box (for maps)

---

## **4️⃣ Step 4: Load All Locality Sub-APIs (Parallel)**

Once `locality_id` is known, frontend will call these **in parallel** 👇

---

### **🔹 Registry Transactions**

GET /api/v1/transactions?locality\_id={id}

---

### **🔹 Price Insights**

GET /api/v1/price-insights/summary?locality\_id={id}  
GET /api/v1/price-insights/by-bhk?locality\_id={id}

---

### **🔹 Trends & Graphs**

GET /api/v1/trends/price?locality\_id={id}\&duration=5y  
GET /api/v1/trends/growth?locality\_id={id}  
GET /api/v1/trends/compare?locality\_id={id}

---

### **🔹 Demand & Supply**

GET /api/v1/demand/overview?locality\_id={id}  
GET /api/v1/supply/overview?locality\_id={id}

---

### **🔹 Properties**

GET /api/v1/properties/buy?locality\_id={id}  
GET /api/v1/properties/rent?locality\_id={id}

---

### **🔹 Societies & Projects**

GET /api/v1/societies?locality\_id={id}  
GET /api/v1/projects?locality\_id={id}

---

### **🔹 Reviews**

GET /api/v1/reviews/locality?locality\_id={id}  
GET /api/v1/reviews/ratings-summary?locality\_id={id}

---

### **🔹 Nearby Areas**

GET /api/v1/nearby-areas?locality\_id={id}

---

## **5️⃣ Step 5: One Combined API (Optional – Recommended)**

To reduce frontend load 👇

GET /api/v1/graphs/dashboard?locality\_id={id}

This API should aggregate:

* price trend graph  
* demand pie  
* supply bar  
* BHK price ranges

---

## **6️⃣ MongoDB Schema (Important for Backend)**

### **`localities`**

{  
  "\_id": "hosur\_road\_blr",  
  "name": "Hosur Road",  
  "city": "Bangalore",  
  "zone": "South Bangalore",  
  "location": {  
    "type": "Point",  
    "coordinates": \[77.6399, 12.8916\]  
  }  
}

---

### **Geo Index (MANDATORY)**

db.localities.createIndex({ location: "2dsphere" })

Used for:

* nearby areas  
* map bounding  
* fast lookup

---

## **7️⃣ Mappls Integration Rules (Tell Developer Clearly)**

✅ Use **Mappls only for**

* map rendering  
* place search  
* reverse geocoding

❌ Do NOT fetch business data from Mappls  
(All prices, trends, reviews come from **our DB**)

---

## **8️⃣ Error Handling Rules**

| Case | Action |
| ----- | ----- |
| Unknown location | Show “Data coming soon” |
| Partial data | Return empty arrays |
| No transactions | Hide registry section |
| Mappls failure | Fallback to cached locality |

---

## **9️⃣ Caching Strategy (IMPORTANT)**

* Cache `place_name → locality_id`  
* Cache price trends (24 hrs)  
* Cache graphs (12 hrs)

Redis key example:

locality:hosur\_road:price\_trend

---

## **🔟 Final Explanation (Send This Line)**

“Mappls is only used to identify the location and coordinates.  
Once coordinates are resolved, backend maps it to our `locality_id` and all locality-related APIs are fetched from our database to render a 99acres-like locality page.”

---

