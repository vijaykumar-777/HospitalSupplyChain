# Project Roadmap

**7 phases** | **13 requirements mapped** | All v1 requirements covered ✓

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Foundation & Data | Generate realistic synthetic hospital supply chain data | GEN-01, GEN-02, GEN-03 | 3 |
| 2 | Backend APIs | Build the core FastAPI application for managing orders and inventory | API-01, API-02 | 3 |
| 3 | Core AI Module | Implement Ollama for delay prediction and disaster analysis | AI-01, AI-02, AI-03 | 3 |
| 4 | External APIs | Integrate GDACS, NewsAPI, ReliefWeb, and OpenRouteService | EXT-01, EXT-02 | 3 |
| 5 | Frontend Dashboards | Build React UI for normal and disaster modes | UI-01, UI-02 | 3 |
| 6 | Live Simulation | Implement automated data progression for demos | SIM-01 | 2 |
| 7 | Integration | Verify end-to-end functionality across all components | All | 3 |

## Phase Details

### Phase 1: Foundation & Data
Goal: Generate realistic synthetic hospital supply chain data
Requirements: GEN-01, GEN-02, GEN-03
Success Criteria:
1. `generate_data.py` writes realistic CSV files for 11 schema tables
2. `seed_db.py` successfully populates SQLite DB without constraint errors
3. Generated data has statistical distributions, not flat randoms

### Phase 2: Backend APIs
Goal: Build the core FastAPI application for managing orders and inventory
Requirements: API-01, API-02
Success Criteria:
1. All CRUD operations on orders, POs, and GRNs function properly
2. APScheduler successfully executes background tasks at defined intervals
3. API documentation (Swagger/Redoc) is accessible and accurate

### Phase 3: Core AI Module
Goal: Implement Ollama for delay prediction and disaster analysis
Requirements: AI-01, AI-02, AI-03
Success Criteria:
1. System successfully queries `qwen2.5:7b` for delay predictions
2. Disaster text parsing reliably produces valid JSON outputs
3. AI predictions log accurately records every inference

### Phase 4: External APIs
Goal: Integrate GDACS, NewsAPI, ReliefWeb, and OpenRouteService
Requirements: EXT-01, EXT-02
Success Criteria:
1. External APIs are polled without hitting rate limits
2. OpenRouteService correctly outputs alternate route GeoJSON
3. Disaster events are deduped and stored in the database

### Phase 5: Frontend Dashboards
**UI hint**: yes
Goal: Build React UI for normal and disaster modes
Requirements: UI-01, UI-02
Success Criteria:
1. Normal dashboard displays orders with accurate delay badges
2. Disaster dashboard dynamically toggles based on active disaster state
3. Leaflet map renders routes correctly

### Phase 6: Live Simulation
Goal: Implement automated data progression for demos
Requirements: SIM-01
Success Criteria:
1. Simulation endpoint successfully advances time/data state
2. Frontend instantly reflects the simulated state changes

### Phase 7: Integration
Goal: Verify end-to-end functionality across all components
Requirements: All
Success Criteria:
1. Complete order lifecycle (PO -> GRN) verified
2. AI triggers properly in response to disaster events
3. No console errors or failed API requests during full simulation flow
