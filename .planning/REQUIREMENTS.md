# Requirements

## v1 Requirements

### Foundation
- [x] **GEN-01**: Generate realistic synthetic data for suppliers, items, orders, and inventory.
- [x] **GEN-02**: Generate synthetic delivery history, purchase orders, and goods receipt notes.
- [x] **GEN-03**: Generate synthetic disaster history events.

### Backend
- [x] **API-01**: Build REST endpoints for orders, POs, GRNs, suppliers, and inventory (FastAPI).
- [x] **API-02**: Implement background scheduler for periodic checks (APScheduler).

### AI & Predictions
- [x] **AI-01**: Integrate Ollama to predict delivery delays based on order context.
- [x] **AI-02**: Integrate Ollama to analyze raw disaster texts and determine severity/radius.
- [x] **AI-03**: Integrate Ollama to predict demand surge and recommend alternate emergency suppliers.

### External Integrations
- [x] **EXT-01**: Fetch disaster alerts periodically from GDACS, ReliefWeb, and NewsAPI.
- [x] **EXT-02**: Calculate alternate supply routes avoiding disaster zones using OpenRouteService.

### Frontend
- [x] **UI-01**: Build a normal operations dashboard showing orders and delays (React).
- [x] **UI-02**: Build a disaster mode dashboard highlighting demand surges, blocked routes, and emergency sourcing.

### Simulation
- [x] **SIM-01**: Create a live simulation layer for automated data state progression (demos).

## v2 Requirements (Deferred)
(None explicitly deferred at this stage, PRD is completely covered)

## Out of Scope
- Real-world production medical data
- Cloud AI APIs (OpenAI/Anthropic)

## Traceability
- Phase 1: GEN-01, GEN-02, GEN-03
- Phase 2: API-01, API-02
- Phase 3: AI-01, AI-02, AI-03
- Phase 4: EXT-01, EXT-02
- Phase 5: UI-01, UI-02
- Phase 6: SIM-01
- Phase 7: All requirements
