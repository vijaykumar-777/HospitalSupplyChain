# Disaster Routing Upgrade & View Response Plan Fix

This plan addresses the user's request for "Google Maps precision" alternate routing and fixing the "View Response Plan" feature by implementing the visual and logic upgrades outlined in the `disaster_route_map_upgrade_plan.md`.

## User Review Required

> [!IMPORTANT]
> The upgrade involves switching from **Leaflet** to **MapLibre GL JS** and **deck.gl**. This is a significant architectural change for the frontend map component.

## Proposed Changes

### [Backend] Logic & Precision

#### [MODIFY] [disaster_pipeline.py](file:///Users/vijaykumarbk/Desktop/NEW%20MAIN%20EL/backend/services/disaster_pipeline.py)
- Refine `build_avoid_polygon` to use more points (64 instead of 24) for a smoother avoidance zone.
- Update `run_disaster_pipeline` to ensure it targets more than just 2 orders in demo mode if available.
- Ensure the disaster location is slightly randomized or derived more realistically from the alert text if possible, though demo consistency is priority.

#### [MODIFY] [external_apis.py](file:///Users/vijaykumarbk/Desktop/NEW%20MAIN%20EL/backend/services/external_apis.py)
- Ensure `get_alternate_route` explicitly requests high-resolution geometry from OpenRouteService.

---

### [Frontend] Visual Upgrade (MapLibre + deck.gl)

#### [MODIFY] [Disaster.jsx](file:///Users/vijaykumarbk/Desktop/NEW%20MAIN%20EL/frontend/src/pages/Disaster.jsx)
- Replace `react-leaflet` with `maplibre-gl` and `@deck.gl/react`.
- Implement layers:
    - `GeoJsonLayer` for the disaster zone (smooth polygon).
    - `PathLayer` for the original (blocked) and alternate (safe) routes.
    - `IconLayer` or `ScatterplotLayer` for suppliers and hospital.
- Fix the "View Response Plan" by ensuring the map correctly centers on the active disaster and displays the "Affected Orders" even if only a few exist.

#### [MODIFY] [package.json](file:///Users/vijaykumarbk/Desktop/NEW%20MAIN%20EL/frontend/package.json)
- Add dependencies: `maplibre-gl`, `@deck.gl/react`, `@deck.gl/layers`, `@turf/turf`.

---

### [UI/UX] Fixing "View Response Plan"

#### [MODIFY] [Layout.jsx](file:///Users/vijaykumarbk/Desktop/NEW%20MAIN%20EL/frontend/src/components/Layout.jsx)
- Ensure the state sync between the Banner and the Disaster page is robust.

## Verification Plan

### Automated Tests
- N/A (UI focused)

### Manual Verification
1. Run `simulateDisaster` and verify the "ACTIVE DISASTER" banner appears.
2. Click "View Response Plan".
3. Verify the MapLibre map loads and centers on the disaster.
4. Verify the alternate route (green/cyan) avoids the red disaster zone.
5. Verify the "Route Decision Panel" displays the correct ETA and risk reduction.
