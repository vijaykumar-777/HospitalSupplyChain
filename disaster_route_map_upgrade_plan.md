# Disaster Route Map Upgrade Plan
## Hospital Supply Chain — Disaster Routing & Alternate Route Visualization

---

## 1. Purpose of This Document

This document contains the complete upgrade plan for improving the disaster map and alternate route visualization in the **Hospital Supply Chain — Delivery Delay & Disaster Prediction System**.

The earlier map implementation used **Leaflet**, but the output was visually unclear for demonstrating disaster zones, blocked routes, and alternate emergency routes. The goal of this upgrade is to make the map look professional, interactive, and academically convincing.

The upgraded map should clearly prove that the system can:

1. Detect a disaster zone.
2. Identify affected suppliers and blocked routes.
3. Generate safer alternate routes.
4. Show the recommended supplier and route clearly.
5. Explain why the alternate route is better.

The map must not look like a decorative dashboard element. It should become the main visual proof of the project.

---

## 2. Problem With the Existing Leaflet Map

The previous Leaflet-based map had these issues:

- Disaster zone was not visually clear.
- Original and alternate routes were hard to distinguish.
- Supplier markers did not communicate enough meaning.
- Route risk was not obvious at first glance.
- The map looked basic and not suitable for a disaster-response system.
- The alternate route did not visually prove that it avoided the affected zone.
- Teachers could not quickly understand what the system was doing.

For this project, the map is not just a UI component. It is a critical explanation layer for the whole system.

---

## 3. Recommended Replacement Stack

Replace the old Leaflet-based map with the following stack:

```txt
MapLibre GL JS + deck.gl + OpenRouteService + Turf.js
```

### 3.1 MapLibre GL JS

Use **MapLibre GL JS** as the main interactive map renderer.

Purpose:

- Display the base map.
- Support smooth zooming and panning.
- Render vector-style map layers.
- Provide a more modern look than basic Leaflet.

Why use it:

- Free and open-source.
- Works well with React.
- Better visual quality than basic Leaflet maps.
- Good for professional dashboard-style maps.

---

### 3.2 deck.gl

Use **deck.gl** for advanced visual layers on top of the map.

Purpose:

- Display disaster polygons.
- Display route lines.
- Display supplier markers.
- Animate alternate routes.
- Show route comparison layers clearly.

Recommended deck.gl layers:

```txt
GeoJsonLayer     → disaster zone polygons and route GeoJSON
PathLayer        → original and alternate route lines
ScatterplotLayer → supplier points and hospital marker
TextLayer        → labels for suppliers, routes, and disaster zones
TripsLayer       → optional animated route movement effect
```

Why use it:

- Strong route visualization.
- Supports animation.
- Makes the map feel like a command-center interface.
- Better for multi-layer data than plain Leaflet.

---

### 3.3 OpenRouteService

Use **OpenRouteService** for route calculation.

Purpose:

- Generate road routes between supplier and hospital.
- Generate alternate routes by avoiding disaster zones.
- Return route geometry as GeoJSON.
- Calculate ETA and distance.

Important feature:

```txt
avoid_polygons
```

This allows the backend to pass a disaster zone polygon to OpenRouteService and request a route that avoids that area.

Example routing logic:

```txt
Supplier location
→ Hospital location
→ Disaster zone polygon
→ OpenRouteService route request with avoid_polygons
→ Alternate route GeoJSON
→ Save in database
→ Display on frontend map
```

---

### 3.4 Turf.js

Use **Turf.js** for geospatial calculations in the frontend or backend.

Purpose:

- Convert disaster radius into a polygon.
- Check if a route intersects a disaster zone.
- Check if a supplier is inside the affected area.
- Calculate distance between points.
- Generate buffer zones.

Useful Turf.js functions:

```txt
turf.circle()
turf.booleanPointInPolygon()
turf.booleanIntersects()
turf.distance()
turf.buffer()
```

---

## 4. Free / Cost Details

This stack is mostly free and suitable for a college project or demo.

| Tool | Free? | Purpose |
|---|---|---|
| MapLibre GL JS | Yes | Interactive map rendering |
| deck.gl | Yes | Advanced map visual layers |
| Turf.js | Yes | Geospatial calculations |
| OpenStreetMap data | Yes | Base geographical map data |
| OpenRouteService | Free tier available | Route calculation and alternate routes |

### Important Note About Map Tiles

MapLibre itself is free, but it needs map tiles or a map style to show the actual map background.

Avoid using Google Maps or paid Mapbox plans for this project unless required, because they may need billing setup.

Recommended free approach:

```txt
MapLibre GL JS for map rendering
OpenStreetMap-based tile provider for base map
OpenRouteService free tier for routing
Cache route GeoJSON in database to avoid repeated API calls
```

---

## 5. Installation Commands

For the React frontend:

```bash
npm install maplibre-gl @deck.gl/react @deck.gl/layers @turf/turf
```

Optional but useful:

```bash
npm install react-map-gl
```

If using Vite + React:

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install maplibre-gl @deck.gl/react @deck.gl/layers @turf/turf axios
```

---

## 6. Updated System Architecture for Map Module

```txt
FastAPI Backend
│
├── Disaster event detection
├── Disaster zone polygon generation
├── Supplier risk detection
├── Original route generation
├── Alternate route generation using ORS avoid_polygons
├── Route risk calculation
└── API response as clean GeoJSON

React Frontend
│
├── MapLibre GL JS base map
├── deck.gl disaster zone layer
├── deck.gl supplier marker layer
├── deck.gl original route layer
├── deck.gl alternate route layer
├── Route decision side panel
└── Disaster analytics tables
```

---

## 7. Backend Responsibilities

The backend should not send scattered map data. It should prepare a clean map-ready response.

Backend must handle:

1. Disaster event location.
2. Disaster affected radius.
3. Disaster zone polygon generation.
4. Supplier status calculation.
5. Original route generation.
6. Route-disaster intersection check.
7. Alternate route generation using OpenRouteService.
8. Route ETA and distance calculation.
9. Route recommendation reasoning.
10. Emergency supplier ranking.

---

## 8. Recommended Backend API Endpoint

Create a dedicated endpoint for the disaster map:

```txt
GET /api/disaster/map-data
```

This endpoint should return all the data needed by the frontend map.

---

## 9. Recommended Map API Response Format

```json
{
  "event": {
    "event_id": "EVT-001",
    "source": "simulated",
    "disaster_type": "flood",
    "severity": 4,
    "location_name": "Mangaluru, Karnataka",
    "lat": 12.9141,
    "lng": 74.8560,
    "affected_radius_km": 120,
    "detected_at": "2026-05-14T10:30:00",
    "summary": "Severe flooding across coastal Karnataka. NH-66 and NH-75 may be blocked.",
    "zone_geojson": {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": []
      },
      "properties": {
        "severity": 4,
        "type": "flood"
      }
    }
  },
  "hospital": {
    "name": "Receiving Hospital",
    "lat": 12.9716,
    "lng": 77.5946,
    "city": "Bengaluru"
  },
  "suppliers": [
    {
      "supplier_id": "SUP-001",
      "name": "MedSupply Chennai",
      "city": "Chennai",
      "lat": 13.0827,
      "lng": 80.2707,
      "status": "safe",
      "reliability_score": 0.93,
      "emergency_certified": true,
      "inside_disaster_zone": false,
      "risk_level": "low"
    }
  ],
  "routes": [
    {
      "route_id": "RTE-001",
      "order_id": "ORD-0482",
      "item_name": "IV Saline",
      "quantity": 500,
      "criticality": "life_critical",
      "supplier_id": "SUP-001",
      "supplier_name": "MedSupply Chennai",
      "original_route_geojson": {
        "type": "FeatureCollection",
        "features": []
      },
      "alternate_route_geojson": {
        "type": "FeatureCollection",
        "features": []
      },
      "original_status": "blocked",
      "disruption_risk": "high",
      "original_eta_hours": 11.2,
      "alternate_eta_hours": 6.5,
      "alternate_distance_km": 342,
      "alternate_mode": "road",
      "risk_reduction_percent": 82,
      "reason": "Original route intersects the flood zone. Alternate route avoids the affected polygon and uses a safer eastern corridor."
    }
  ]
}
```

---

## 10. Disaster Zone Geometry Logic

The disaster zone should not only be a simple frontend circle. It should be converted into a real polygon.

### Backend or frontend logic using Turf.js equivalent

```js
const disasterCenter = [lng, lat];
const radius = affected_radius_km;

const disasterPolygon = turf.circle(disasterCenter, radius, {
  steps: 64,
  units: "kilometers"
});
```

This polygon can then be used for:

```txt
1. Rendering the disaster zone on the map.
2. Checking whether suppliers are inside the affected area.
3. Checking if routes intersect the affected area.
4. Passing as avoid_polygons to OpenRouteService.
```

---

## 11. OpenRouteService Alternate Route Logic

The backend should call OpenRouteService like this:

```python
async def get_alternate_route(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    avoid_polygon_geojson: dict,
    ors_api_key: str
):
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {
        "Authorization": ors_api_key,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [origin_lng, origin_lat],
            [dest_lng, dest_lat]
        ],
        "options": {
            "avoid_polygons": avoid_polygon_geojson
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=body, headers=headers)

    return response.json()
```

Important:

- Always send coordinates as `[lng, lat]`, not `[lat, lng]`.
- Store the returned route GeoJSON in the database.
- Do not call ORS repeatedly on every page refresh.
- Cache the route result in `affected_routes.alternate_route_geojson`.

---

## 12. Database Table Changes

The existing `affected_routes` table already supports most of this.

Recommended fields:

```txt
affected_routes
├── route_id
├── event_id
├── supplier_id
├── order_id
├── original_route_geojson
├── original_route_name
├── is_blocked
├── disruption_risk
├── alternate_route_geojson
├── alternate_mode
├── original_eta_hours
├── alternate_eta_hours
├── alternate_distance_km
├── risk_reduction_percent
├── ai_route_reason
└── created_at
```

If `original_route_geojson` is missing, add it. This is important because the frontend must compare the original blocked route and the alternate safe route.

---

## 13. Frontend Map Layers

The frontend should render the map using separate visual layers.

Recommended components:

```txt
frontend/src/components/map/
├── EmergencyMap.jsx
├── DisasterZoneLayer.jsx
├── SupplierMarkersLayer.jsx
├── RouteComparisonLayer.jsx
├── AnimatedRouteLayer.jsx
├── MapLegend.jsx
├── RouteDecisionPanel.jsx
└── MapControls.jsx
```

---

## 14. Layer Details

### 14.1 Base Map Layer

Use MapLibre GL JS.

Style:

```txt
Dark professional map style
Low saturation
High contrast overlays
No unnecessary visual clutter
```

---

### 14.2 Disaster Zone Layer

Show:

- Semi-transparent red polygon.
- Orange warning border.
- Disaster label.
- Severity badge.

Visual rule:

```txt
Severity 1–2 → yellow/orange
Severity 3 → orange
Severity 4–5 → red
```

---

### 14.3 Supplier Marker Layer

Supplier marker color rules:

```txt
Green  → safe supplier
Yellow → delayed or at-risk supplier
Red    → inside disaster zone / unreachable
Purple → emergency-certified supplier
Gold   → government reserve supplier
```

Each supplier popup should show:

```txt
Supplier name
City
Reliability score
Emergency certified: Yes/No
Inside disaster zone: Yes/No
Available categories
Estimated dispatch time
```

---

### 14.4 Hospital Marker Layer

Hospital marker should be visually larger than supplier markers.

Show:

```txt
Hospital name
City
Current emergency status
Number of critical items at stockout risk
```

---

### 14.5 Original Route Layer

Original route should be shown as:

```txt
Thin red dashed line
Blocked/high-risk label
Warning icon where it intersects the disaster zone
```

This is important because the teacher must immediately understand why the original route is bad.

---

### 14.6 Alternate Route Layer

Alternate route should be shown as:

```txt
Thick green or cyan glowing line
Animated movement dots
Clear “Recommended Route” label
ETA label
```

This route should visually avoid the red disaster polygon.

---

### 14.7 Map Legend

Add a legend in the bottom-left corner.

Legend items:

```txt
Blue icon     → Hospital
Green dot     → Safe supplier
Yellow dot    → At-risk supplier
Red dot       → Blocked supplier
Purple dot    → Emergency supplier
Red dashed    → Original blocked route
Green solid   → Recommended alternate route
Red polygon   → Disaster affected zone
Orange border → Warning buffer
```

---

## 15. Disaster Dashboard Layout

Use a command-center layout.

```txt
┌──────────────────────────────────────────────────────────────┐
│ DISASTER MODE ACTIVE — Flood — Severity 4 — Coastal Karnataka │
├──────────────────────────────────────┬───────────────────────┤
│                                      │ Route Decision Panel   │
│                                      │                       │
│        Interactive Emergency Map     │ Supplier: MedSupply   │
│                                      │ Original: Blocked     │
│        - Disaster zone               │ Alternate ETA: 6.5h   │
│        - Supplier markers            │ Risk reduced: 82%     │
│        - Original route              │                       │
│        - Alternate route             │ [Approve Route]       │
│                                      │ [Supplier Details]    │
├──────────────────────────────────────┴───────────────────────┤
│ Affected Orders | Emergency Suppliers | Demand Surge Table    │
└──────────────────────────────────────────────────────────────┘
```

---

## 16. Route Decision Panel

The route decision panel is extremely important. It explains the map result in plain English.

Show this information:

```txt
Selected Order ID
Item Name
Quantity
Criticality
Original Supplier
Recommended Supplier
Original Route Status
Original ETA
Alternate ETA
Alternate Distance
Route Mode
Risk Reduction %
Supplier Reliability
Emergency Certification
AI Explanation
```

Example:

```txt
Recommended Route: MedSupply Chennai → Bengaluru Hospital

Original Route:
Status: Blocked
Reason: Route passes through flood-affected NH-75 region
ETA: 11.2 hours
Risk: High

Alternate Route:
Status: Safe
Mode: Road
ETA: 6.5 hours
Distance: 342 km
Avoided Zone: Yes
Supplier Reliability: 93%
Emergency Certified: Yes

AI Reason:
This supplier is outside the affected radius, has high reliability, and the route avoids the flood polygon while maintaining the lowest ETA.
```

---

## 17. Bottom Analytics Section

Add three tabs below the map.

### 17.1 Affected Orders Tab

Columns:

```txt
Order ID
Item
Supplier
Route Risk
Original ETA
Alternate ETA
Status
Action
```

---

### 17.2 Emergency Suppliers Tab

Columns:

```txt
Rank
Supplier
City
Reliability
Emergency Certified
Estimated Delivery Hours
Reason
```

---

### 17.3 Demand Surge Tab

Columns:

```txt
Item
Current Stock
Surge Multiplier
Stockout Hours
Recommended Emergency Order Quantity
Urgency
```

---

## 18. Demo Flow

Use the manual disaster simulation feature for demonstration.

Recommended demo flow:

```txt
1. Start on the normal dashboard.
2. Show normal suppliers and pending orders.
3. Click Demo Controls.
4. Trigger “Coastal Karnataka Flood”.
5. Disaster banner appears.
6. Map zooms to the disaster zone.
7. Red affected polygon appears.
8. Original routes become red dashed lines.
9. Alternate safe route appears in green/cyan.
10. Route panel explains why the alternate route is selected.
11. Affected orders and emergency suppliers update automatically.
```

This makes the project feel dynamic and realistic.

---

## 19. Demo Controls Panel

Add a floating demo control button at the bottom-right.

Panel content:

```txt
Demo Controls
├── Trigger Kerala Flood
├── Trigger Bengaluru Building Collapse
├── Trigger Andhra Cyclone
├── Reset Disaster Mode
├── Simulation Status: Running/Stopped
├── Tick Count
└── Last Updated Time
```

Only show this panel when:

```txt
DEMO_MODE=true
```

---

## 20. Styling Requirements

Use a professional emergency command-center style.

Visual style:

```txt
Dark navy background
Glassmorphism panels
Thin grid texture
High contrast map overlays
Clean typography
No clutter
No generic AI-dashboard look
```

Avoid:

```txt
Too many random colors
Flat plain cards
Default Leaflet appearance
Unclear route lines
Tiny markers
Weak labels
Crowded popups
```

---

## 21. Color System

Recommended colors:

```txt
Background: dark navy / near black
Main panels: translucent navy glass
Hospital: blue
Safe supplier: green
At-risk supplier: yellow/orange
Blocked supplier: red
Emergency supplier: purple/gold
Original route: red dashed
Alternate route: green/cyan solid
Disaster zone: transparent red
Warning border: orange
```

---

## 22. Why This Upgrade Will Impress Evaluators

This upgrade makes the project easier to understand because the map directly answers:

```txt
Where is the disaster?
Which suppliers are affected?
Which route is blocked?
Which alternate route is safer?
Which supplier is recommended?
Why did the system make this decision?
```

Instead of only saying the system recommends an alternate route, the dashboard visually proves it.

---

## 23. Implementation Priority

If time is limited, implement in this order:

### Priority 1 — Must Have

```txt
MapLibre map
Disaster zone polygon
Supplier markers
Original route red dashed line
Alternate route green/cyan line
Route decision panel
Legend
```

### Priority 2 — Should Have

```txt
Animated route movement
Route intersection warning icon
Route comparison metrics
Affected orders table
Emergency suppliers table
```

### Priority 3 — Nice to Have

```txt
TripsLayer animation
Timeline slider
Weather overlay
Live simulation feed
3D terrain effect
```

---

## 24. Final Frontend Generation Prompt

Use the following prompt in an AI frontend generator such as Google Stitch.

```txt
Design a professional emergency logistics dashboard for a Hospital Supply Chain Disaster Prediction System.

The main focus is the Disaster Routing Map. Do not create a basic Leaflet-style map. Create a modern command-center style interactive map layout using a dark navy dashboard theme with high contrast route visualization.

Project context:
The system predicts hospital supply delivery delays and disaster disruptions. During a disaster, it must show affected suppliers, blocked routes, disaster zones, and recommended alternate routes for emergency medical supplies.

Create the Disaster Dashboard page with the following layout:

1. Top Alert Header
- Full-width red emergency banner
- Text: “DISASTER MODE ACTIVE”
- Show disaster type, severity, location, affected radius, detected time
- Add a “SIMULATED” badge if the event source is simulated
- Add buttons: “Refresh Routes”, “Reset Disaster”, “View AI Summary”

2. Main Map Section
- Large interactive map occupying 65–70% width
- Dark professional map style
- Show hospital marker with a blue hospital icon
- Show supplier markers:
  - Green = safe supplier
  - Yellow = at risk supplier
  - Red = blocked/unreachable supplier
  - Purple/gold = emergency-certified supplier
- Show disaster zone as a semi-transparent red polygon
- Show outer warning buffer as orange border
- Show original route as thin red dashed line
- Show alternate route as thick glowing green/blue line
- Add small animated movement dots along the alternate route
- Add blocked-road icon where original route intersects disaster zone
- Add map legend in bottom-left
- Add zoom controls, layer toggle, and route filter controls

3. Route Decision Panel on the right
- Show selected order ID, item name, quantity, criticality
- Show original supplier and alternate supplier
- Show original route status: BLOCKED / HIGH RISK
- Show alternate ETA, distance, route mode, reliability score
- Show “Why this route?” AI explanation card
- Show risk reduction score as a large percentage
- Add button: “Approve Emergency Route”
- Add button: “View Supplier Details”

4. Bottom Analytics Section
Create three tabs:
- Affected Orders
- Emergency Suppliers
- Demand Surge

Affected Orders table:
Columns: Order ID, Item, Supplier, Route Risk, Original ETA, Alternate ETA, Status

Emergency Suppliers table:
Columns: Rank, Supplier, City, Reliability, Emergency Certified, Estimated Delivery Hours, Reason

Demand Surge table:
Columns: Item, Current Stock, Surge Multiplier, Stockout Hours, Recommended Order Qty

5. Visual Style
- Dark navy background
- Glassmorphism panels
- Thin grid texture in the background
- High contrast map overlays
- Clean typography
- Do not make it look like a generic AI-generated dashboard
- Use realistic spacing and professional emergency command center styling
- The map must clearly prove that the alternate route avoids the disaster zone

6. Demo Controls
Add a floating “Demo Controls” button at bottom-right.
Panel should include:
- Trigger Kerala Flood
- Trigger Bengaluru Building Collapse
- Trigger Andhra Cyclone
- Reset Disaster Mode
- Simulation Running status
- Last updated timestamp

Most important:
The map should be visually clear enough that a teacher can immediately understand:
1. where the disaster is,
2. which route is blocked,
3. which alternate route is safer,
4. which supplier is recommended,
5. why the system made that decision.
```

---

## 25. Final Recommendation

For this project, use:

```txt
MapLibre GL JS + deck.gl + OpenRouteService + Turf.js
```

Do not rely on a basic Leaflet map if the project evaluation depends on route clarity.

The final dashboard should feel like an emergency medical logistics control room, not a simple marker map.

The strongest version of the feature is:

```txt
A disaster routing map where the disaster zone is visible, the blocked original route is shown in red, the safer alternate route is highlighted and animated, suppliers are color-coded by risk, and a side panel explains the routing decision in simple terms.
```
