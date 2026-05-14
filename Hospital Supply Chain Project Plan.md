# Hospital Supply Chain — Delivery Delay & Disaster Prediction System
### Complete Project Execution Plan

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Data Schema — All Tables](#4-data-schema--all-tables)
5. [API Keys & External Services](#5-api-keys--external-services)
6. [Project Structure (Folder Layout)](#6-project-structure-folder-layout)
7. [Phase 1 — Synthetic Data Generation](#phase-1--synthetic-data-generation)
8. [Phase 2 — Backend API (FastAPI)](#phase-2--backend-api-fastapi)
9. [Phase 3 — AI Module (Ollama)](#phase-3--ai-module-ollama)
10. [Phase 4 — External API Integrations](#phase-4--external-api-integrations)
11. [Phase 5 — Frontend Dashboard (React)](#phase-5--frontend-dashboard-react)
12. [Phase 6 — Disaster Mode](#phase-6--disaster-mode)
13. [Phase 7 — Integration & Testing](#phase-7--integration--testing)
14. [Phase 8 — Live Simulation Layer ⭐ Demo Addition](#phase-8--live-simulation-layer--demo-addition)
15. [Phase 9 — Manual Disaster Simulation Endpoint ⭐ Demo Addition](#phase-9--manual-disaster-simulation-endpoint--demo-addition)
16. [Execution Timeline (Gantt)](#execution-timeline-gantt)
17. [Ollama Prompt Templates](#ollama-prompt-templates)
18. [Key Business Logic Rules](#key-business-logic-rules)
19. [Appendix A — Realistic Synthetic Data Generation ⭐ Professor Fix](#appendix-a--realistic-synthetic-data-generation--professor-fix)

---

## 1. Project Overview

### Problem Statement
Hospitals order medical supplies from multiple suppliers. Two critical failure modes exist:

- **Normal mode** — deliveries get delayed without warning, causing stockouts of life-critical items.
- **Disaster mode** — when a natural or man-made disaster strikes, demand surges unpredictably, suppliers become unreachable, and delivery routes get blocked.

### What This System Does
- Predicts delivery delays per order (before they happen) and estimates the revised ETA
- Suggests alternate suppliers when a delay is detected
- Monitors real-time disaster alerts (GDACS, ReliefWeb, NewsAPI)
- During a disaster: predicts demand surge per item category, identifies blocked routes, and recommends emergency suppliers with fastest alternate routes
- Presents everything on a dual-mode React dashboard (Normal view + Disaster alert view)

### Scope
- **Actors:** One hospital ↔ Multiple suppliers
- **Supply types:** Medicines, surgical instruments, medical consumables, equipment
- **AI:** Ollama (local LLM) for all inference — no cloud AI costs
- **Data:** Fully synthetic (generated with Python + Faker)

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      REACT FRONTEND                         │
│   Normal Dashboard  │  Order Detail  │  Disaster Dashboard  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP (REST)
┌───────────────────────────▼─────────────────────────────────┐
│                     FASTAPI BACKEND                         │
│                                                             │
│  /orders   /predictions   /suppliers   /disaster   /routes  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Scheduler   │  │  AI Module   │  │  External APIs   │  │
│  │ (APScheduler)│  │  (Ollama)    │  │ GDACS/ReliefWeb  │  │
│  │ 15-min polls │  │  Prompts +   │  │ NewsAPI / ORS    │  │
│  │              │  │  JSON parser │  │ Nominatim        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │               SQLite / PostgreSQL                   │    │
│  │  suppliers │ items │ orders │ inventory │ ...        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow — Normal Mode
```
Order placed → FastAPI stores order → Ollama predicts delay
→ If delayed: compute new ETA + suggest alternate suppliers
→ Periodic re-check every 24h → Dashboard updates
```

### Data Flow — Disaster Mode
```
Scheduler polls GDACS + ReliefWeb + NewsAPI every 15 min
→ New event found → Raw text sent to Ollama
→ Ollama infers: type, severity (1–5), affected radius
→ Parallel predictions:
    [A] Demand surge per item category
    [B] Delivery disruption per pending order
→ OpenRouteService computes alternate routes
→ Dashboard switches to DISASTER MODE
```

---

## 3. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React 18 + Vite | Fast dev, component-based |
| Styling | Tailwind CSS | Rapid utility-first styling |
| Maps | Leaflet.js + React-Leaflet | Free, open-source maps |
| Backend | Python 3.11 + FastAPI | Async, auto-docs, fast |
| ORM | SQLAlchemy + Alembic | Schema migrations |
| Database | SQLite (dev) / PostgreSQL (prod) | Simple → scalable |
| AI | Ollama (Qwen2.5 or Llama3) | Local, free, no API key |
| Scheduler | APScheduler | Background periodic jobs |
| Data gen | Python + Faker + Pandas | Synthetic data |
| HTTP client | httpx (async) | For external API calls |
| Env config | python-dotenv | API key management |

---

## 4. Data Schema — All Tables

### 4.1 Normal Mode Tables

#### `suppliers`
| Field | Type | Constraints | Description |
|---|---|---|---|
| supplier_id | UUID | PK | Unique identifier |
| name | VARCHAR(200) | NOT NULL | Company name |
| city | VARCHAR(100) | NOT NULL | Operating city |
| state | VARCHAR(100) | NOT NULL | State |
| lat | FLOAT | NOT NULL | Latitude (for disaster zone check) |
| lng | FLOAT | NOT NULL | Longitude (for disaster zone check) |
| reliability_score | FLOAT | 0.0–1.0 | Historical on-time delivery rate |
| avg_lead_days | INTEGER | NOT NULL | Average days from order to delivery |
| supply_categories | JSON | NOT NULL | Array: ['medicines','instruments','consumables','equipment'] |
| is_emergency_certified | BOOLEAN | DEFAULT false | Can operate during disasters |
| is_govt_reserve | BOOLEAN | DEFAULT false | Central/state government medical store |
| contact_email | VARCHAR(200) | | |
| contact_phone | VARCHAR(20) | | |
| created_at | DATETIME | DEFAULT now() | |

---

#### `items`
| Field | Type | Constraints | Description |
|---|---|---|---|
| item_id | UUID | PK | |
| name | VARCHAR(300) | NOT NULL | e.g. Paracetamol 500mg, IV Cannula 18G |
| category | ENUM | NOT NULL | medicine / instrument / consumable / equipment |
| criticality | ENUM | NOT NULL | low / medium / high / life_critical |
| unit | VARCHAR(50) | NOT NULL | tablets, units, pcs, litres, vials |
| disaster_surge_category | VARCHAR(100) | | trauma / burn / respiratory / general — used in disaster mode |
| typical_monthly_demand | INTEGER | | Hospital's average monthly consumption |
| created_at | DATETIME | DEFAULT now() | |

---

#### `orders`
| Field | Type | Constraints | Description |
|---|---|---|---|
| order_id | UUID | PK | |
| item_id | UUID | FK → items | |
| supplier_id | UUID | FK → suppliers | |
| quantity | INTEGER | NOT NULL | Units ordered |
| order_date | DATETIME | NOT NULL | When order was placed |
| expected_delivery_date | DATE | NOT NULL | Promised delivery date |
| status | ENUM | NOT NULL | pending / in_transit / delivered / delayed / cancelled |
| is_emergency_order | BOOLEAN | DEFAULT false | Flagged during disaster mode |
| triggered_by_disaster_event_id | UUID | FK → disaster_events, nullable | Links order to a disaster if raised during one |
| created_at | DATETIME | DEFAULT now() | |

---

#### `delivery_history`
| Field | Type | Constraints | Description |
|---|---|---|---|
| delivery_id | UUID | PK | |
| order_id | UUID | FK → orders | |
| supplier_id | UUID | FK → suppliers | |
| item_id | UUID | FK → items | |
| expected_date | DATE | NOT NULL | |
| actual_date | DATE | | NULL if not yet delivered |
| delay_days | INTEGER | | Negative = early, 0 = on time, positive = late |
| delay_reason | VARCHAR(200) | | weather / stock_shortage / transport / disaster / customs / other |
| season | ENUM | | monsoon / summer / winter / post_monsoon |
| created_at | DATETIME | DEFAULT now() | |

---

#### `inventory`
| Field | Type | Constraints | Description |
|---|---|---|---|
| inventory_id | UUID | PK | |
| item_id | UUID | FK → items, UNIQUE | One row per item |
| current_stock | INTEGER | NOT NULL | Current units in hospital |
| reorder_level | INTEGER | NOT NULL | Place new order below this threshold |
| max_capacity | INTEGER | NOT NULL | Maximum storage capacity |
| daily_consumption_normal | FLOAT | NOT NULL | Average units consumed per day (normal) |
| daily_consumption_disaster | FLOAT | NOT NULL | Estimated surge consumption per day |
| last_updated | DATETIME | DEFAULT now() | |

---

#### `purchase_orders` ⭐ Real-world procurement stage
In real hospital supply chains a Purchase Order (PO) is a formal procurement document raised *before* an order is dispatched to a supplier. It carries approval authority, budget codes, and payment terms — separate from the operational order tracking. This table reflects that.

| Field | Type | Constraints | Description |
|---|---|---|---|
| po_id | UUID | PK | |
| po_number | VARCHAR(50) | NOT NULL, UNIQUE | Human-readable e.g. PO-2025-00482 |
| order_id | UUID | FK → orders | Links to the operational order |
| raised_by | VARCHAR(200) | NOT NULL | Staff who raised the PO |
| approved_by | VARCHAR(200) | | Approving authority (store manager / CMO) |
| approval_date | DATETIME | | When PO was approved |
| approval_status | ENUM | NOT NULL | draft / pending_approval / approved / rejected |
| budget_code | VARCHAR(100) | NOT NULL | Department budget allocation e.g. PHARM-2025-Q3 |
| payment_terms | ENUM | NOT NULL | advance / NET30 / NET60 |
| payment_status | ENUM | NOT NULL | pending / paid / overdue |
| total_value_inr | FLOAT | NOT NULL | Total order value in INR |
| created_at | DATETIME | DEFAULT now() | |

---

#### `goods_receipt_note` ⭐ Real-world receiving stage
In every real hospital, when supplies arrive they go through a receiving and quality inspection step (GRN process) before stock is updated in inventory. Without this, the supply chain ends at "delivered" which is incomplete from a domain standpoint.

| Field | Type | Constraints | Description |
|---|---|---|---|
| grn_id | UUID | PK | |
| grn_number | VARCHAR(50) | NOT NULL, UNIQUE | e.g. GRN-2025-00891 |
| order_id | UUID | FK → orders | |
| po_id | UUID | FK → purchase_orders | |
| received_date | DATETIME | NOT NULL | Actual date goods arrived at hospital |
| received_by | VARCHAR(200) | NOT NULL | Store staff who received the shipment |
| inspected_by | VARCHAR(200) | NOT NULL | Quality inspection staff |
| ordered_qty | INTEGER | NOT NULL | What was originally ordered |
| received_qty | INTEGER | NOT NULL | Units actually received (may differ) |
| accepted_qty | INTEGER | NOT NULL | Units accepted after inspection |
| rejected_qty | INTEGER | NOT NULL | Units rejected |
| quality_status | ENUM | NOT NULL | accepted / partially_accepted / rejected |
| rejection_reason | VARCHAR(300) | | damaged / expired / wrong_item / quantity_mismatch / packaging_defect |
| added_to_inventory | BOOLEAN | DEFAULT false | Whether stock was updated post-inspection |
| batch_number | VARCHAR(100) | | Manufacturer batch/lot number |
| expiry_date | DATE | | For medicines and consumables |
| created_at | DATETIME | DEFAULT now() | |

---

### 4.2 Disaster Mode Tables

#### `disaster_events`
| Field | Type | Constraints | Description |
|---|---|---|---|
| event_id | UUID | PK | |
| source | ENUM | NOT NULL | gdacs / reliefweb / newsapi |
| external_event_id | VARCHAR(200) | | ID from the source API (for deduplication) |
| disaster_type | ENUM | NOT NULL | flood / earthquake / cyclone / fire / collapse / other |
| severity | INTEGER | 1–5 | AI inferred from raw text |
| location_name | VARCHAR(300) | NOT NULL | City/region name |
| lat | FLOAT | | Epicenter latitude |
| lng | FLOAT | | Epicenter longitude |
| affected_radius_km | INTEGER | | AI inferred radius of impact |
| detected_at | DATETIME | NOT NULL | When system first detected this event |
| is_active | BOOLEAN | DEFAULT true | Still ongoing? |
| raw_text | TEXT | NOT NULL | Original API payload fed to Ollama |
| ai_summary | TEXT | | Ollama's plain-English summary |
| created_at | DATETIME | DEFAULT now() | |

---

#### `disaster_predictions`
| Field | Type | Constraints | Description |
|---|---|---|---|
| pred_id | UUID | PK | |
| event_id | UUID | FK → disaster_events | |
| item_id | UUID | FK → items | |
| surge_multiplier | FLOAT | NOT NULL | e.g. 3.2 means 3.2× normal demand |
| urgency_window_hours | INTEGER | NOT NULL | 6 / 24 / 48 |
| predicted_stockout_in_hours | FLOAT | | Based on current stock ÷ surge consumption |
| ai_reasoning | TEXT | | Ollama's plain-English explanation |
| created_at | DATETIME | DEFAULT now() | |

---

#### `affected_routes`
| Field | Type | Constraints | Description |
|---|---|---|---|
| route_id | UUID | PK | |
| event_id | UUID | FK → disaster_events | |
| supplier_id | UUID | FK → suppliers | |
| order_id | UUID | FK → orders, nullable | If tied to a specific order |
| original_route_name | VARCHAR(200) | | e.g. NH-44 or "Chennai–Bengaluru highway" |
| is_blocked | BOOLEAN | DEFAULT false | |
| disruption_risk | ENUM | | low / medium / high / blocked |
| alternate_route_geojson | JSON | | GeoJSON from OpenRouteService |
| alternate_mode | ENUM | | road / rail / air |
| alternate_eta_hours | FLOAT | | ETA via alternate route |
| created_at | DATETIME | DEFAULT now() | |

---

#### `disaster_history` *(synthetic — for AI context)*
| Field | Type | Constraints | Description |
|---|---|---|---|
| hist_id | UUID | PK | |
| disaster_type | ENUM | NOT NULL | flood / earthquake / cyclone / fire / collapse |
| severity | INTEGER | 1–5 | |
| location_name | VARCHAR(300) | NOT NULL | |
| year | INTEGER | NOT NULL | |
| items_most_affected | JSON | NOT NULL | Array of item categories that spiked |
| avg_supply_delay_added_days | FLOAT | | How much delivery times worsened |
| demand_multipliers | JSON | | Per-category surge data e.g. {"trauma":4.2,"respiratory":2.8} |
| notes | TEXT | | Free-text context for AI |

---

#### `ai_predictions_log`
| Field | Type | Constraints | Description |
|---|---|---|---|
| log_id | UUID | PK | |
| prediction_type | ENUM | NOT NULL | delivery_delay / disaster_severity / demand_surge / route_disruption |
| input_payload | JSON | NOT NULL | Exact prompt context sent to Ollama |
| output_payload | JSON | NOT NULL | Raw Ollama JSON response |
| order_id | UUID | FK → orders, nullable | |
| event_id | UUID | FK → disaster_events, nullable | |
| model_used | VARCHAR(100) | | e.g. qwen2.5:7b |
| latency_ms | INTEGER | | Inference time |
| created_at | DATETIME | DEFAULT now() | |

---

## 5. API Keys & External Services

| Service | Used For | Cost | Key Required | Sign Up |
|---|---|---|---|---|
| **NewsAPI** | Real-time local/man-made disaster news | Free — 100 req/day | Yes | newsapi.org |
| **GDACS** | Natural disaster alerts (flood, earthquake, cyclone) | Free | No | gdacs.org/xml.aspx (RSS) |
| **ReliefWeb API** | UN humanitarian disaster reports | Free | No | api.reliefweb.int |
| **OpenRouteService (ORS)** | Alternate route calculation avoiding disaster zones | Free — 2000 req/day | Yes | openrouteservice.org |
| **Nominatim (OSM)** | City/address ↔ lat/lng geocoding | Free | No | nominatim.openstreetmap.org |
| **Ollama** | All AI inference (delay, severity, surge, routes) | Free — runs locally | No | ollama.com |

### `.env` file template
```env
# NewsAPI
NEWS_API_KEY=your_newsapi_key_here

# OpenRouteService
ORS_API_KEY=your_ors_key_here

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# DB
DATABASE_URL=sqlite:///./hospital_supply.db

# App
POLL_INTERVAL_MINUTES=15
HOSPITAL_LAT=12.9716
HOSPITAL_LNG=77.5946
HOSPITAL_CITY=Bengaluru
```

---

## 6. Project Structure (Folder Layout)

```
hospital-supply-chain/
│
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── database.py                # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── supplier.py
│   │   ├── item.py
│   │   ├── order.py
│   │   ├── purchase_order.py          ← NEW real-world procurement stage
│   │   ├── goods_receipt_note.py      ← NEW real-world receiving stage
│   │   ├── inventory.py
│   │   ├── delivery_history.py
│   │   ├── disaster_event.py
│   │   ├── disaster_prediction.py
│   │   ├── affected_route.py
│   │   ├── disaster_history.py
│   │   └── ai_predictions_log.py
│   ├── schemas/                   # Pydantic request/response models
│   │   ├── order.py
│   │   ├── supplier.py
│   │   ├── disaster.py
│   │   └── prediction.py
│   ├── routers/
│   │   ├── orders.py              # /orders endpoints
│   │   ├── suppliers.py           # /suppliers endpoints
│   │   ├── inventory.py           # /inventory endpoints
│   │   ├── predictions.py         # /predictions endpoints
│   │   └── disaster.py            # /disaster endpoints
│   ├── services/
│   │   ├── ai_service.py          # Ollama prompt builder + parser
│   │   ├── disaster_service.py    # GDACS + ReliefWeb + NewsAPI polling
│   │   ├── route_service.py       # OpenRouteService integration
│   │   ├── geocoding_service.py   # Nominatim lat/lng resolution
│   │   └── scheduler.py           # APScheduler job definitions
│   ├── data/
│   │   ├── generate_data.py       # Synthetic data generator script
│   │   └── seed_db.py             # Seeds generated data into DB
│   ├── alembic/                   # DB migrations
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── api/
│   │   │   └── client.js          # Axios instance + all API calls
│   │   ├── pages/
│   │   │   ├── OrdersPage.jsx     # Main order list view
│   │   │   ├── OrderDetailPage.jsx
│   │   │   ├── SuppliersPage.jsx
│   │   │   └── DisasterPage.jsx   # Disaster mode dashboard
│   │   ├── components/
│   │   │   ├── OrderTable.jsx
│   │   │   ├── DelayBadge.jsx
│   │   │   ├── AlternateSuppliersPanel.jsx
│   │   │   ├── DisasterAlert.jsx
│   │   │   ├── SurgePredictionTable.jsx
│   │   │   ├── DisasterMap.jsx    # Leaflet map component
│   │   │   └── RoutePanel.jsx
│   │   ├── hooks/
│   │   │   ├── useOrders.js
│   │   │   ├── useDisaster.js
│   │   │   └── usePolling.js      # Auto-refresh hook
│   │   └── utils/
│   │       ├── formatDate.js
│   │       └── riskColor.js       # green/yellow/red logic
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── data_output/                   # Generated CSVs from generate_data.py
│   ├── suppliers.csv
│   ├── items.csv
│   ├── orders.csv
│   ├── purchase_orders.csv            ← NEW
│   ├── goods_receipt_notes.csv        ← NEW
│   ├── delivery_history.csv
│   ├── inventory.csv
│   ├── inventory_snapshots.csv        ← NEW (90-day sawtooth simulation output)
│   ├── disaster_history.csv
│   └── disaster_events_sample.csv
│
└── README.md
```

---

## Phase 1 — Synthetic Data Generation

**Goal:** Generate realistic fake data for all 11 tables using Python + Faker + NumPy. Data must use statistically realistic distributions and inter-field correlations — not flat random values — so it passes academic scrutiny. See Appendix A for the full reasoning behind each distribution choice.

### Steps

#### Step 1.1 — Setup
```bash
pip install faker pandas numpy uuid scipy
```

#### Step 1.2 — What to generate and how

**suppliers (30 records)**
- 25 regular suppliers across Indian cities (Mumbai, Chennai, Delhi, Hyderabad, Pune, Kolkata, Ahmedabad)
- 4 emergency-certified suppliers
- 1 government reserve (e.g. CMSS — Central Medical Services Society)
- Reliability scores: **bimodal distribution** — 70% in good tier (normal, mean=0.87, std=0.05), 30% in poor tier (normal, mean=0.58, std=0.08), clipped to [0.30, 0.99]
- `avg_lead_days`: scaled to distance from hospital — `1 + (distance_km / 300)` + normal noise (std=0.5), minimum 1 day
- `supply_categories`: randomly assign 1–3 categories per supplier, weighted by city (e.g. Mumbai suppliers more likely to carry pharmaceuticals, Chennai more instruments)

**items (80 records)**
- 25 medicines (e.g. Paracetamol, Amoxicillin, IV Saline, Insulin, Morphine)
- 20 surgical instruments (e.g. Scalpel handle, Forceps, Retractor set)
- 25 consumables (e.g. Nitrile gloves, Syringes 5ml, IV cannula, Gauze rolls)
- 10 equipment (e.g. Pulse oximeter, Infusion pump, BP monitor)
- Criticality distribution: 10% life_critical, 30% high, 40% medium, 20% low
- `disaster_surge_category`: assign trauma/burn/respiratory/general based on item type
- `typical_monthly_demand`: **log-normal distribution** (mean=4.5, sigma=0.8) — a few high-volume items, many low-volume ones

**orders (500 records)**
- Supplier selected per order using **weighted affinity**: `weight = distance_weight × category_weight × reliability_score` — closer, relevant, reliable suppliers get picked more often
- `quantity`: **log-normal distribution** (mean=4.5, sigma=0.8) — peaks around 90 units, tail to 2000+
- `order_date`: past 12 months with **higher frequency on weekdays** (Mon–Fri weight=1.0, Sat=0.5, Sun=0.2)
- `expected_delivery_date`: `order_date + lead_days` where lead_days = supplier avg ± normal noise

**delivery_history (500 records, one per order)**
- Delay generated using **conditional exponential distribution** based on season AND supplier tier:
  - Monsoon + poor supplier: `exponential(scale=6)`, cap at 21 days
  - Monsoon + good supplier: `exponential(scale=2.5)`
  - Non-monsoon + poor supplier: `exponential(scale=3)`
  - Non-monsoon + good supplier: `exponential(scale=1.2)`
- 65% of deliveries: delay=0 (on time), 20%: delay 1–3 days, 10%: delay 4–10 days, 5%: delay -1 to -2 (early)
- `delay_reason`: correlated to season — monsoon orders get weather/transport reasons more often
- `season`: derived from order_date month (Jun–Sep=monsoon, Oct–Nov=post_monsoon, Dec–Feb=winter, Mar–May=summer)

**purchase_orders (500 records, one per order)**
- `po_number`: sequential e.g. PO-2025-00001
- `approval_status`: 90% approved, 5% pending, 5% rejected
- `payment_terms`: 60% NET30, 30% NET60, 10% advance
- `total_value_inr`: `quantity × unit_price` where unit_price varies by item category
- `raised_by` / `approved_by`: generated names using Faker

**goods_receipt_note (for all delivered orders)**
- `received_qty`: 95% = ordered_qty, 5% = ordered_qty × uniform(0.85, 0.99) (short shipment)
- `quality_status`: 88% accepted, 8% partially_accepted, 4% rejected
- `rejection_reason`: weighted — damaged (40%), expired (30%), wrong_item (20%), packaging_defect (10%)
- `batch_number`: random alphanumeric e.g. BT-2025-48291
- `expiry_date`: for medicines/consumables only — uniform 6–36 months from received_date

**inventory (80 records, one per item)**
- Generated using **sawtooth simulation** over 90 days:
  - Start at max_capacity
  - Each day: subtract `daily_consumption × seasonal_multiplier × day_of_week_multiplier`
  - When stock hits reorder_level: add a random restock quantity
  - `current_stock` = value at day 90 of simulation
- Intentionally leave 10 items below reorder_level for dashboard visual interest
- `daily_consumption_disaster`: 2x–5x normal, depending on disaster_surge_category

**disaster_history (50 records — pure synthetic past events)**
- Cover past 20 years of India disasters (Kerala floods 2018, Odisha cyclone, Gujarat earthquake, etc.)
- `demand_multipliers`: JSON like `{"trauma": 4.2, "burn": 3.1, "respiratory": 2.4, "general": 1.8}`
- `avg_supply_delay_added_days`: correlated to severity — severity 5 adds more delay than severity 2

#### Step 1.3 — Seasonal and weekly multipliers config
```python
SEASONAL_MULTIPLIER = {
    "respiratory": {"monsoon": 1.4, "winter": 1.6, "summer": 0.9, "post_monsoon": 1.1},
    "trauma":      {"monsoon": 1.3, "winter": 1.0, "summer": 1.1, "post_monsoon": 1.2},
    "burn":        {"monsoon": 1.0, "winter": 1.1, "summer": 1.3, "post_monsoon": 1.0},
    "general":     {"monsoon": 1.1, "winter": 1.1, "summer": 1.0, "post_monsoon": 1.0},
}

DAY_OF_WEEK_MULTIPLIER = [1.10, 1.15, 1.10, 1.05, 1.00, 0.75, 0.65]  # Mon–Sun
```

#### Step 1.4 — Output
Run `generate_data.py` → writes CSVs to `/data_output/`
Run `seed_db.py` → reads CSVs → inserts into SQLite via SQLAlchemy

---

## Phase 2 — Backend API (FastAPI)

**Goal:** Build all REST endpoints the frontend will consume.

### Steps

#### Step 2.1 — Project setup
```bash
pip install fastapi uvicorn sqlalchemy alembic httpx apscheduler python-dotenv pydantic
```

#### Step 2.2 — Database setup
- Define all SQLAlchemy models (one file per table)
- Run Alembic migrations to create tables
- Run seed script

#### Step 2.3 — Endpoints to build

**Orders**
```
POST   /api/orders                        Create order → auto-creates draft PO → triggers AI delay prediction
GET    /api/orders                        List all orders (with filters: status, supplier, date range)
GET    /api/orders/{order_id}             Single order detail
GET    /api/orders/{order_id}/prediction  Delay prediction for this order
PATCH  /api/orders/{order_id}/status      Update order status
```

**Purchase Orders**
```
GET    /api/purchase-orders               List all POs with approval status
GET    /api/purchase-orders/{po_id}       Single PO detail
PATCH  /api/purchase-orders/{po_id}/approve   Approve a PO
PATCH  /api/purchase-orders/{po_id}/reject    Reject a PO with reason
```

**Goods Receipt Notes**
```
POST   /api/grn                           Record a new goods receipt (updates inventory if accepted)
GET    /api/grn                           List all GRNs
GET    /api/grn/{grn_id}                  Single GRN detail
GET    /api/grn/order/{order_id}          GRN for a specific order
```

**Suppliers**
```
GET    /api/suppliers                     List all suppliers
GET    /api/suppliers/{supplier_id}       Supplier detail + delivery history stats
GET    /api/suppliers/alternates          Query: ?item_id=X — returns ranked alternate suppliers
```

**Inventory**
```
GET    /api/inventory                     Full inventory list with stock status
GET    /api/inventory/{item_id}           Single item stock detail
```

**Predictions**
```
GET    /api/predictions/log               AI prediction history log
POST   /api/predictions/recheck-all       Manually trigger re-prediction on all pending orders
```

**Disaster**
```
GET    /api/disaster/events               List all detected disaster events (active first)
GET    /api/disaster/events/{event_id}    Event detail with all predictions + routes
GET    /api/disaster/active               Returns current active event (if any) — frontend polls this
POST   /api/disaster/trigger-check        Manually trigger a disaster detection poll
GET    /api/disaster/surge-predictions    Demand surge table for active disaster
GET    /api/disaster/routes               Affected routes + alternates for active disaster
```

#### Step 2.4 — Scheduler jobs (APScheduler)
```python
# Every 15 minutes
scheduler.add_job(poll_disaster_apis, 'interval', minutes=15)

# Every 24 hours
scheduler.add_job(recheck_all_pending_orders, 'interval', hours=24)

# Every hour (if disaster active)
scheduler.add_job(refresh_disaster_predictions, 'interval', hours=1, 
                  condition=lambda: active_disaster_exists())
```

---

## Phase 3 — AI Module (Ollama)

**Goal:** Build the prompt templates, call Ollama, parse JSON output reliably.

### Steps

#### Step 3.1 — Ollama setup
```bash
ollama pull qwen2.5:7b        # Main model for prediction
ollama pull qwen2.5:1.5b      # Lightweight fallback if slow
```

#### Step 3.2 — Four prompt chains to implement

**Prompt A — Delivery delay prediction (called on every new order)**

Input context:
- Supplier name, city, reliability score, avg lead days, past delay rate (last 6 months)
- Item name, criticality, category
- Order quantity vs supplier's typical capacity
- Days since order placed vs expected lead time
- Current season (monsoon / summer / etc.)
- Current inventory level for this item (urgency flag if below reorder level)

Expected JSON output:
```json
{
  "is_delayed": true,
  "confidence": 0.82,
  "extra_days": 4,
  "new_eta": "2025-08-18",
  "risk_level": "high",
  "reason": "Supplier has 34% monsoon delay rate. Item is life_critical with only 2 days of stock remaining."
}
```

---

**Prompt B — Disaster severity analysis (called when new event detected)**

Input context:
- Raw text from GDACS/ReliefWeb/NewsAPI
- Hospital location (lat/lng)
- Distance from disaster epicenter (computed before prompt)

Expected JSON output:
```json
{
  "disaster_type": "flood",
  "severity": 4,
  "affected_radius_km": 120,
  "supply_routes_likely_blocked": true,
  "estimated_casualties": "high",
  "suppliers_at_risk_ids": ["uuid1", "uuid2"],
  "summary": "Severe flooding in coastal Karnataka. Major highways NH-66 and NH-75 likely blocked. High casualty count expected."
}
```

---

**Prompt C — Demand surge prediction (called once per active disaster, per item)**

Input context:
- Disaster type + severity
- Item name, category, criticality, disaster_surge_category
- Current stock level + daily consumption (normal and disaster)
- Past disaster_history records for same disaster type

Expected JSON output:
```json
{
  "surge_multiplier": 3.8,
  "urgency_window_hours": 24,
  "predicted_stockout_in_hours": 18.5,
  "recommended_emergency_order_qty": 5000,
  "reasoning": "Flood severity 4 historically causes 3–5× trauma supply surge. Current stock lasts ~18h at disaster consumption rate."
}
```

---

**Prompt D — Emergency supplier ranking (called when delay or disaster detected)**

Input context:
- Item needed (name, category, quantity required)
- List of alternate suppliers (name, city, lat/lng, reliability, is_emergency_certified, avg_lead_days)
- Affected zone (lat/lng + radius) — to exclude blocked suppliers
- Disaster type (if active)

Expected JSON output:
```json
{
  "ranked_suppliers": [
    {
      "supplier_id": "uuid3",
      "rank": 1,
      "recommended": true,
      "reason": "MedSupply Chennai is 240km outside flood zone, emergency-certified, 6h lead time, reliability 0.93"
    },
    {
      "supplier_id": "uuid7",
      "rank": 2,
      "recommended": true,
      "reason": "CMSS Bengaluru (govt reserve) can dispatch within 4h but stock confirmation needed"
    }
  ]
}
```

#### Step 3.3 — Robust JSON parsing
Ollama sometimes wraps JSON in markdown. Always strip it:
```python
import json, re

def parse_ollama_json(raw: str) -> dict:
    cleaned = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: extract first {...} block
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse Ollama response: {raw[:200]}")
```

#### Step 3.4 — Log every prediction
After every Ollama call, write to `ai_predictions_log` table with input, output, latency, and model name.

---

## Phase 4 — External API Integrations

### Step 4.1 — GDACS (no key needed)
```python
import httpx
from xml.etree import ElementTree as ET

async def fetch_gdacs_alerts():
    url = "https://www.gdacs.org/xml.aspx"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    root = ET.fromstring(resp.text)
    events = []
    for item in root.findall('.//item'):
        events.append({
            "title": item.findtext('title'),
            "description": item.findtext('description'),
            "pubDate": item.findtext('pubDate'),
            "link": item.findtext('link')
        })
    return events
```

### Step 4.2 — ReliefWeb API (no key needed)
```python
async def fetch_reliefweb_alerts():
    url = "https://api.reliefweb.int/v1/disasters"
    params = {
        "appname": "hospital-supply-chain",
        "filter[field]": "country.name",
        "filter[value]": "India",
        "limit": 10,
        "sort[]": "date:desc"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
    return resp.json()["data"]
```

### Step 4.3 — NewsAPI
```python
async def fetch_news_disaster_alerts(api_key: str):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "disaster OR flood OR earthquake OR cyclone OR fire India hospital",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": api_key
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
    return resp.json()["articles"]
```

### Step 4.4 — Deduplication logic
Before creating a `disaster_events` record, check:
1. Same `external_event_id` from source? Skip.
2. Same `disaster_type` + `location_name` + within 48h? Skip.
3. Otherwise, insert and trigger prediction chain.

### Step 4.5 — OpenRouteService (alternate routes)
```python
async def get_alternate_route(
    origin_lat: float, origin_lng: float,
    dest_lat: float, dest_lng: float,
    avoid_polygon_geojson: dict,
    ors_api_key: str
):
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {"Authorization": ors_api_key, "Content-Type": "application/json"}
    body = {
        "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]],
        "options": {"avoid_polygons": avoid_polygon_geojson}
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=body, headers=headers)
    return resp.json()
```

### Step 4.6 — Nominatim geocoding
```python
async def geocode_city(city_name: str) -> tuple[float, float]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name + ", India", "format": "json", "limit": 1}
    headers = {"User-Agent": "hospital-supply-chain/1.0"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers=headers)
    data = resp.json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    raise ValueError(f"Could not geocode: {city_name}")
```

---

## Phase 5 — Frontend Dashboard (React)

### Step 5.1 — Setup
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install tailwindcss axios react-leaflet leaflet react-router-dom date-fns
```

### Step 5.2 — Pages and what they show

**Page 1: Orders (`/orders`)**
- Table with columns: Order ID, Item, Supplier, Qty, Expected Date, Status, Risk Level, Action
- Color coding: green = on time, yellow = at risk, red = delayed
- Filters: by status, supplier, date range, criticality
- Click row → goes to Order Detail page
- Top bar shows: total orders, delayed count, at-risk count

**Page 2: Order Detail (`/orders/:id`)**
- Shows full order info
- AI prediction card: "Delayed by 4 days (82% confidence)" with reasoning
- New ETA prominently shown
- Alternate Suppliers panel: ranked list with reliability, lead time, reason
- Delivery history chart for this supplier + item combination

**Page 3: Suppliers (`/suppliers`)**
- Card grid of all suppliers
- Each card: name, city, reliability score (progress bar), categories, emergency badge
- Click → supplier detail with past performance chart

**Page 4: Inventory (`/inventory`)**
- Table: item, category, criticality, current stock, reorder level, status
- Items below reorder level highlighted in red
- Days-of-stock-remaining column (computed: current_stock ÷ daily_consumption)

**Page 5: Disaster Dashboard (`/disaster`) — activates automatically**
- Full-width map (Leaflet): red circle = affected zone, supplier pins colored by status, route overlays
- Severity badge: "SEVERITY 4 — FLOOD — Coastal Karnataka"
- Two panels side by side:
  - Left: Demand Surge table (item → current stock → surge multiplier → hours to stockout)
  - Right: Emergency Suppliers ranked list
- Bottom: Affected orders table with disruption risk + revised ETA
- Auto-refreshes every 60 seconds

### Step 5.3 — Auto disaster mode trigger
Frontend polls `GET /api/disaster/active` every 60 seconds.
If response contains an active event → shows a red banner at top of every page + link to Disaster Dashboard.

### Step 5.4 — API client (`/src/api/client.js`)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
});

export const getOrders = (filters) => api.get('/orders', { params: filters });
export const getOrderDetail = (id) => api.get(`/orders/${id}`);
export const getOrderPrediction = (id) => api.get(`/orders/${id}/prediction`);
export const getAlternateSuppliers = (itemId) => api.get('/suppliers/alternates', { params: { item_id: itemId } });
export const getActiveDisaster = () => api.get('/disaster/active');
export const getDisasterEvent = (id) => api.get(`/disaster/events/${id}`);
export const getSurgePredictions = () => api.get('/disaster/surge-predictions');
export const getAffectedRoutes = () => api.get('/disaster/routes');
```

---

## Phase 6 — Disaster Mode

This phase wires together the detection engine, AI predictions, and route service.

### Step 6.1 — Disaster detection pipeline
```
Every 15 min:
1. fetch_gdacs_alerts() → deduplicate → if new → insert disaster_events row
2. fetch_reliefweb_alerts() → same
3. fetch_news_disaster_alerts() → same
4. For each new event:
   a. geocode_city(event.location_name) → get lat/lng
   b. compute distance from hospital to epicenter
   c. if distance < 500km → trigger prediction chain
```

### Step 6.2 — Prediction chain on new disaster event
```
1. Build Prompt B context → call Ollama → parse severity/radius/route_blocked
2. For each item in inventory:
   a. Build Prompt C context → call Ollama → get surge_multiplier + stockout_hours
   b. Insert into disaster_predictions
3. For each pending order's supplier:
   a. Check if supplier lat/lng is within affected_radius_km
   b. If yes → call ORS for alternate route
   c. Insert into affected_routes
4. Build Prompt D → rank emergency suppliers for top-5 most critical items
5. Mark disaster_event as active → frontend picks it up on next poll
```

### Step 6.3 — Disaster zone geometry
To check if a supplier is in the disaster zone:
```python
from math import radians, sin, cos, sqrt, atan2

def haversine_km(lat1, lng1, lat2, lng2) -> float:
    R = 6371
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def is_in_disaster_zone(supplier_lat, supplier_lng, event_lat, event_lng, radius_km) -> bool:
    return haversine_km(supplier_lat, supplier_lng, event_lat, event_lng) <= radius_km
```

---

## Phase 7 — Integration & Testing

### Step 7.1 — Unit tests (pytest)
- `test_ai_service.py` — mock Ollama responses, test JSON parser with malformed outputs
- `test_disaster_detection.py` — mock GDACS/ReliefWeb/NewsAPI, test deduplication
- `test_haversine.py` — zone containment checks with known coordinates
- `test_route_service.py` — mock ORS, test GeoJSON parsing

### Step 7.2 — Integration tests
- Place an order → verify prediction created in DB
- Simulate disaster event insert → verify prediction chain runs → verify affected_routes populated
- Call `/api/disaster/active` → verify correct response format

### Step 7.3 — Manual testing checklist
- [ ] Generate and seed all synthetic data
- [ ] All 9 API endpoints return correct data
- [ ] Ollama produces valid JSON for all 4 prompt types
- [ ] Disaster polling runs on schedule (check logs)
- [ ] Frontend loads orders page with correct color coding
- [ ] Order detail shows prediction + alternate suppliers
- [ ] Disaster dashboard shows map with correct zone circle
- [ ] Surge prediction table populates correctly
- [ ] Auto-refresh works (60s frontend poll)

### Step 7.4 — Running the full stack
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 3: Start frontend
cd frontend
npm run dev
```

---

## Phase 8 — Live Simulation Layer ⭐ Demo Addition

**Goal:** Make the dashboard feel alive during a demo. A background script continuously nudges inventory levels, progresses order statuses, and occasionally introduces realistic delays — so reviewers see a dynamic system, not a frozen snapshot.

**Why this matters for demo:** Nothing kills a demo faster than a static dashboard. With this running, every time you refresh during your presentation something has changed — stock levels are dropping, an order just flipped to "delayed", a new prediction fired. It looks like a real production system.

### Step 8.1 — Create `simulator.py`

Location: `backend/services/simulator.py`

This script runs as a background APScheduler job, firing every **3 minutes** during demo mode.

#### What it does on each tick:

**1. Consume inventory**
For every item in `inventory`, subtract a small random amount from `current_stock`:
```python
daily = item.daily_consumption_normal
tick_consumption = round(random.uniform(0.05, 0.15) * daily, 1)  # ~5–15% of daily use per tick
item.current_stock = max(0, item.current_stock - tick_consumption)
```
If `current_stock` drops below `reorder_level` → auto-create a new pending order for that item (pick the supplier with highest reliability for that category).

**2. Progress order statuses**
For each `pending` order where `order_date` is > 1 day ago → flip to `in_transit`.
For each `in_transit` order where `expected_delivery_date` is today or past:
- 70% chance → flip to `delivered`, create `delivery_history` record with `delay_days = 0`
- 20% chance → flip to `delayed`, create `delivery_history` with `delay_days = random(1, 5)`, trigger Prompt A re-prediction
- 10% chance → stay `in_transit` (still en route)

**3. Randomly degrade one supplier's reliability (occasionally)**
Every 5th tick, pick one random non-emergency supplier and nudge their `reliability_score` down by 0.02–0.05. This causes the AI to start flagging their orders as higher risk on next re-check. Resets after 10 ticks.

**4. Log simulation activity**
Write each tick's actions to a `simulation_log` table (simple: tick_time, action_type, description) so the demo can optionally show "what just changed" in a live feed panel on the frontend.

### Step 8.2 — New table: `simulation_log`

| Field | Type | Description |
|---|---|---|
| log_id | UUID | PK |
| tick_time | DATETIME | When this action occurred |
| action_type | ENUM | inventory_consumed / order_progressed / supplier_degraded / auto_order_created |
| description | TEXT | Human-readable e.g. "IV Saline stock dropped to 45 units — auto-reorder triggered" |
| affected_entity_id | UUID | The order/item/supplier affected |

### Step 8.3 — New API endpoint

```
GET  /api/simulation/log          Returns last 20 simulation actions (for live feed panel)
POST /api/simulation/start        Starts the simulator job (demo mode on)
POST /api/simulation/stop         Stops the simulator job (demo mode off)
GET  /api/simulation/status       Returns { running: true/false, tick_count: N, last_tick: datetime }
```

### Step 8.4 — Frontend: Live Feed Panel

Add a collapsible "Live Activity" sidebar panel on the Orders page that polls `GET /api/simulation/log` every 15 seconds and shows a scrolling list:

```
🟡  2 min ago   IV Saline stock fell below reorder level — auto-order created
🔴  5 min ago   Order #ORD-0482 flipped to DELAYED — AI re-prediction triggered
🟢  8 min ago   Order #ORD-0391 delivered on time — history updated
⚠️  11 min ago  MedCorp Mumbai reliability score dropped to 0.61
```

### Step 8.5 — Demo mode toggle

Add a `DEMO_MODE=true` flag in `.env`. When true:
- Simulator runs every 3 minutes
- Live Feed panel is visible on frontend
- Disaster simulation endpoint (Phase 9) is enabled

When false (production):
- Simulator is disabled
- Live Feed panel hidden
- Disaster simulation endpoint returns 403

---

## Phase 9 — Manual Disaster Simulation Endpoint ⭐ Demo Addition

**Goal:** Trigger the full disaster prediction pipeline instantly during a demo, without waiting for a real GDACS event. One API call flips the dashboard into disaster mode with realistic data.

**Why this matters for demo:** Real disasters won't happen on cue. This lets you say "let me show you what happens when a flood hits coastal Karnataka" and hit a button — the entire disaster dashboard populates in real time in front of your audience.

### Step 9.1 — New endpoint

```
POST /api/disaster/simulate
```

**Request body:**
```json
{
  "disaster_type": "flood",
  "severity": 4,
  "location_name": "Mangaluru, Karnataka",
  "lat": 12.9141,
  "lng": 74.8560,
  "affected_radius_km": 120,
  "description": "Severe flooding across coastal Karnataka following heavy monsoon rainfall. NH-66 and NH-75 reported submerged."
}
```

**What it does internally (same pipeline as real detection):**

```
1. Validate DEMO_MODE=true (return 403 if not)
2. Insert a new disaster_events row with source="simulated"
3. Run Prompt B (severity analysis) using the provided description as raw_text
4. For each item in inventory → run Prompt C (demand surge)
5. For each pending/in_transit order → check if supplier in zone → run ORS alternate route
6. Run Prompt D (emergency supplier ranking) for top 5 critical items
7. Mark event as is_active=true
8. Return { event_id, summary, suppliers_at_risk_count, items_at_risk_count }
```

**Response:**
```json
{
  "event_id": "uuid",
  "disaster_type": "flood",
  "severity": 4,
  "summary": "Severe flooding in coastal Karnataka. 3 suppliers in affected zone. 12 items predicted to hit critical stockout within 24h.",
  "suppliers_at_risk_count": 3,
  "items_at_risk_count": 12,
  "dashboard_url": "/disaster"
}
```

Frontend receives this, redirects to `/disaster` — full disaster dashboard populates automatically.

### Step 9.2 — Reset endpoint

```
POST /api/disaster/simulate/reset
```

Clears the simulated event (sets `is_active=false`), resets all `disaster_predictions` for that event, and returns the dashboard to normal mode. Essential for running the demo multiple times.

### Step 9.3 — Pre-built demo scenarios

Create a file `backend/data/demo_scenarios.json` with 3 ready-to-use disaster scenarios:

```json
[
  {
    "name": "Kerala Floods (Severe)",
    "disaster_type": "flood",
    "severity": 5,
    "location_name": "Kochi, Kerala",
    "lat": 9.9312,
    "lng": 76.2673,
    "affected_radius_km": 150,
    "description": "Catastrophic flooding across central Kerala. All major highways blocked. Mass casualty event underway at multiple sites."
  },
  {
    "name": "Bengaluru Building Collapse (Moderate)",
    "disaster_type": "collapse",
    "severity": 3,
    "location_name": "Bengaluru, Karnataka",
    "lat": 12.9716,
    "lng": 77.5946,
    "affected_radius_km": 30,
    "description": "Partial collapse of a commercial complex in central Bengaluru. 200+ reported trapped. Trauma and surgical supplies in high demand."
  },
  {
    "name": "Andhra Cyclone (Major)",
    "disaster_type": "cyclone",
    "severity": 4,
    "location_name": "Visakhapatnam, Andhra Pradesh",
    "lat": 17.6868,
    "lng": 83.2185,
    "affected_radius_km": 200,
    "description": "Category 4 cyclone making landfall near Visakhapatnam. Coastal districts severely affected. Respiratory and waterborne disease supplies critical."
  }
]
```

### Step 9.4 — Frontend: Demo Control Panel

Add a small "Demo Controls" floating button (bottom-right corner, only visible when `DEMO_MODE=true`) that opens a panel with:
- Three scenario buttons (one per `demo_scenarios.json` entry)
- A "Reset Disaster" button
- Simulation status (running/stopped + tick count)

This lets you run the entire demo from the UI without touching the terminal.

```
┌─────────────────────────────┐
│  🎮  Demo Controls          │
├─────────────────────────────┤
│  Trigger Disaster:          │
│  [Kerala Floods]            │
│  [Bengaluru Collapse]       │
│  [Andhra Cyclone]           │
├─────────────────────────────┤
│  [Reset Disaster Mode]      │
│  Simulation: ● Running      │
│  Ticks: 14 | Last: 2m ago   │
└─────────────────────────────┘
```

### Step 9.5 — Updated folder structure additions

```
backend/
├── services/
│   ├── simulator.py              ← NEW Phase 8
│   └── demo_service.py           ← NEW Phase 9 (scenario loader + reset logic)
├── routers/
│   ├── simulation.py             ← NEW /api/simulation/* endpoints
│   └── disaster.py               ← UPDATED: add /simulate and /simulate/reset
├── data/
│   └── demo_scenarios.json       ← NEW Phase 9

frontend/src/components/
├── LiveFeedPanel.jsx             ← NEW Phase 8
└── DemoControlPanel.jsx          ← NEW Phase 9
```

---

## Execution Timeline (Gantt)

```
Week 1
  Day 1–2   Environment setup + DB models + Alembic migrations
  Day 3–4   Synthetic data generator (generate_data.py + seed_db.py)
  Day 5     All FastAPI endpoints skeleton (return dummy data first)

Week 2
  Day 1–2   Ollama prompt A (delay prediction) + JSON parser
  Day 3     Ollama prompt B (disaster severity)
  Day 4     Ollama prompt C (demand surge)
  Day 5     Ollama prompt D (emergency supplier ranking)

Week 3
  Day 1     GDACS + ReliefWeb integration
  Day 2     NewsAPI integration + deduplication logic
  Day 3     OpenRouteService + Nominatim integration
  Day 4     APScheduler jobs wired to detection + prediction chain
  Day 5     Backend integration test — full disaster pipeline end-to-end

Week 4
  Day 1–2   React: Orders page + Order detail page
  Day 3     React: Suppliers page + Inventory page
  Day 4–5   React: Disaster dashboard (map + surge table + routes)

Week 5
  Day 1     Auto-disaster mode trigger (frontend polling)
  Day 2     Phase 8: simulator.py + simulation_log table + /api/simulation/* endpoints
  Day 3     Phase 8: LiveFeedPanel component + frontend polling
  Day 4     Phase 9: /api/disaster/simulate + reset + demo_scenarios.json
  Day 5     Phase 9: DemoControlPanel component + end-to-end demo run
```

---

## Ollama Prompt Templates

### Prompt A — Delivery delay prediction
```
You are a hospital supply chain AI. Predict if this delivery will be delayed.

ORDER DETAILS:
- Item: {item_name} (Category: {category}, Criticality: {criticality})
- Supplier: {supplier_name}, {supplier_city}
- Supplier reliability score: {reliability_score} (0=worst, 1=best)
- Supplier past delay rate (last 6 months): {past_delay_rate}%
- Average past delays: {avg_past_delay_days} days
- Order quantity: {quantity} {unit}
- Order placed: {order_date}
- Expected delivery: {expected_delivery_date}
- Days remaining: {days_remaining}
- Current season: {season}
- Current hospital stock for this item: {current_stock} {unit} (reorder level: {reorder_level})

Respond ONLY with valid JSON, no markdown, no explanation:
{
  "is_delayed": true/false,
  "confidence": 0.0-1.0,
  "extra_days": integer,
  "new_eta": "YYYY-MM-DD",
  "risk_level": "low/medium/high/critical",
  "reason": "one sentence explanation"
}
```

### Prompt B — Disaster severity
```
You are a hospital supply chain AI analyzing disaster alerts.

HOSPITAL LOCATION: {hospital_city} ({hospital_lat}, {hospital_lng})
DISTANCE TO EVENT: {distance_km} km

RAW ALERT TEXT:
{raw_alert_text}

SUPPLIER LOCATIONS:
{supplier_list_json}

Respond ONLY with valid JSON, no markdown:
{
  "disaster_type": "flood/earthquake/cyclone/fire/collapse/other",
  "severity": 1-5,
  "affected_radius_km": integer,
  "supply_routes_likely_blocked": true/false,
  "estimated_casualties": "low/medium/high/catastrophic",
  "suppliers_at_risk_ids": ["uuid1", "uuid2"],
  "summary": "two sentence plain English summary"
}
```

### Prompt C — Demand surge
```
You are a hospital supply chain AI predicting disaster demand surge.

DISASTER: {disaster_type}, Severity {severity}/5
ITEM: {item_name} (Surge category: {disaster_surge_category}, Criticality: {criticality})
CURRENT STOCK: {current_stock} {unit}
NORMAL DAILY USE: {daily_consumption_normal} {unit}/day
DISASTER DAILY USE (estimated): {daily_consumption_disaster} {unit}/day

HISTORICAL REFERENCE (similar past disasters):
{disaster_history_json}

Respond ONLY with valid JSON, no markdown:
{
  "surge_multiplier": float,
  "urgency_window_hours": 6/24/48,
  "predicted_stockout_in_hours": float,
  "recommended_emergency_order_qty": integer,
  "reasoning": "one sentence"
}
```

### Prompt D — Emergency supplier ranking
```
You are a hospital supply chain AI. Rank emergency suppliers for a critical item.

ITEM NEEDED: {item_name}, Quantity: {quantity}, Criticality: {criticality}
ACTIVE DISASTER: {disaster_type}, Severity {severity} at ({disaster_lat}, {disaster_lng}), radius {radius_km}km

AVAILABLE SUPPLIERS (outside disaster zone):
{suppliers_json}

Rank by: proximity to hospital, reliability, emergency certification, lead time.
Respond ONLY with valid JSON, no markdown:
{
  "ranked_suppliers": [
    {
      "supplier_id": "uuid",
      "rank": 1,
      "estimated_delivery_hours": float,
      "recommended": true/false,
      "reason": "one sentence"
    }
  ]
}
```

---

## Key Business Logic Rules

1. **Order → Prediction always happens** — every new order triggers Prompt A immediately on creation.

2. **Periodic re-check** — all `pending` and `in_transit` orders are re-evaluated every 24h. If a previously on-time order now shows delay risk (e.g. supplier's recent deliveries got worse), status updates automatically.

3. **Disaster threshold** — only trigger disaster mode if `distance_from_hospital < 500km` AND `severity >= 3`. Minor events far away do not activate disaster mode.

4. **Supplier exclusion during disaster** — any supplier whose `haversine_distance(supplier, epicenter) < affected_radius_km` is automatically excluded from alternate supplier suggestions.

5. **Stockout alert** — if `predicted_stockout_in_hours < 24` for a life_critical item during a disaster, the order is auto-flagged as `is_emergency_order = true`.

6. **Deduplication** — same event from multiple sources (e.g. same flood appears in GDACS + NewsAPI) should create only ONE `disaster_events` row. Match on: same disaster_type + location within 50km + within 48h window.

7. **AI log always written** — even if prediction fails or Ollama is unreachable, write a log entry with the error. Never silently drop a prediction attempt.

8. **Transport mode selection logic for alternate routes:**
   - Flood → prefer rail or air (roads likely submerged)
   - Earthquake → prefer road via wide detour (rail lines may be damaged)
   - Fire/collapse → road reroute only (localized, rail unaffected)
   - Cyclone → air suspended, prefer road if distance < 300km, else rail

9. **Simulator only runs in DEMO_MODE** — `DEMO_MODE=true` in `.env` must be set for `simulator.py` and `/api/disaster/simulate` to be active. In production these are locked out (403 on simulate, scheduler job not registered).

10. **Simulated disaster events are tagged** — `disaster_events.source = "simulated"` distinguishes them from real GDACS/ReliefWeb/NewsAPI events. The frontend can optionally show a "SIMULATED" badge on the disaster banner so demo reviewers understand what's happening.

11. **Reset is always clean** — `POST /api/disaster/simulate/reset` must set `is_active=false` on the event AND delete all `disaster_predictions` and `affected_routes` rows linked to that event. A dirty reset that leaves stale prediction rows will cause the dashboard to show ghost data on the next simulate call.

13. **Order → PO → GRN is the correct hospital supply chain flow** — every order must have a corresponding Purchase Order (with approval) before it's dispatched to the supplier. When goods arrive, a GRN must be created and quality-checked before inventory is updated. The flow is strictly: `Order placed → PO raised → PO approved → Supplier dispatches → GRN created → Inventory updated`.

14. **Inventory only updates via GRN** — stock levels must never be incremented directly from order status changes. The only valid trigger for a stock increase is `goods_receipt_note.added_to_inventory = true` after quality inspection. This reflects real hospital store management practice.

15. **Rejected GRN triggers re-order** — if a GRN's `quality_status = rejected` and the item is `life_critical` or `high` criticality, the system auto-creates a new order with `is_emergency_order = true` and flags it for immediate AI prediction.

16. **PO approval gates dispatch** — an order should not be flagged as `in_transit` until its linked PO has `approval_status = approved`. Orders with pending or rejected POs stay in `pending` status regardless of supplier action.

---

*Document version: 1.2 — Updated with realistic synthetic data generation (Appendix A), Purchase Orders table, Goods Receipt Note table, corresponding API endpoints, and 4 new business logic rules reflecting real hospital procurement flow*
*Stack: React + FastAPI + Ollama + SQLite + GDACS + ReliefWeb + NewsAPI + OpenRouteService*

---

## Appendix A — Realistic Synthetic Data Generation ⭐ Professor Fix

This appendix documents **why** each statistical distribution was chosen for data generation. This is the section that addresses the professor's feedback that the synthetic data generation approach was not realistic.

### A.1 What was wrong with naive random generation

Naive generation (e.g. `random.uniform(0.3, 0.99)` for reliability scores, `random.randint(1, 10)` for delay days) produces data with these tell-tale signs of fakeness:

- **Flat histograms** — every value equally likely, which never happens in real supply chains
- **No correlation between fields** — delay days unrelated to season or supplier quality
- **No temporal patterns** — demand same on Monday as Sunday, same in monsoon as summer
- **No realistic tails** — real delay distributions have a heavy tail (most on time, a few very late)
- **No supplier-item affinity** — random supplier assignment ignores geography and specialization

A professor or domain expert immediately identifies these patterns and flags the data as academically unsound.

### A.2 Distribution choices and justification

| Field | Naive approach | Realistic approach | Justification |
|---|---|---|---|
| `reliability_score` | `uniform(0.3, 0.99)` | Bimodal: 70% normal(0.87, 0.05) + 30% normal(0.58, 0.08) | Suppliers in real markets cluster into reliable and unreliable tiers — there is no even spread |
| `delay_days` | `randint(0, 10)` | Conditional exponential — scale varies by season × supplier tier | Delays follow an exponential distribution: most zero, a few large. Scale depends on monsoon season and supplier quality |
| `order_quantity` | `randint(50, 500)` | Log-normal(mean=4.5, sigma=0.8) | Order quantities are right-skewed — many small routine orders, occasional large bulk orders |
| `avg_lead_days` | `randint(2, 14)` | `1 + (distance_km / 300)` + normal noise | Lead time is physically constrained by distance — a supplier 900km away cannot deliver in 2 days |
| `order_date` frequency | Uniform across 365 days | Weighted by day of week (Mon=1.1, Sun=0.2) | Hospitals raise orders predominantly on weekdays; weekend ordering is rare |
| `daily_consumption` | Random between min/max | Base × seasonal_multiplier × day_of_week_multiplier | Consumption follows known seasonal patterns (respiratory items spike in winter, trauma in monsoon) |
| `current_stock` | `randint(reorder, max)` | Sawtooth simulation over 90 days | Real stock follows a sawtooth wave: high after delivery, drains linearly, spikes on restock |
| Supplier selection per order | Random | Weighted: `distance_weight × category_weight × reliability` | Real procurement teams prefer nearby, specialized, reliable suppliers — not random selection |

### A.3 Seasonal multiplier table

```
                 Monsoon  Post-Monsoon  Winter  Summer
Respiratory      1.40     1.10          1.60    0.90
Trauma           1.30     1.20          1.00    1.10
Burn             1.00     1.00          1.10    1.30
General          1.10     1.00          1.10    1.00
```

**Reasoning:**
- Respiratory spikes in winter (cold, flu) and monsoon (infections, waterborne disease)
- Trauma spikes in monsoon (road accidents increase on wet roads) and post-monsoon
- Burn spikes in summer (heat-related incidents, fire accidents)
- General supplies follow mild seasonal variation

### A.4 Delay distribution by scenario

```
Scenario                          Distribution          Avg delay  Max cap
Monsoon + poor supplier (r<0.65)  exponential(scale=6)  6 days     21 days
Monsoon + good supplier (r≥0.65)  exponential(scale=2.5) 2.5 days  14 days
Non-monsoon + poor supplier       exponential(scale=3)   3 days     14 days
Non-monsoon + good supplier       exponential(scale=1.2) 1.2 days   7 days
```

**Why exponential?** Delivery delays in logistics are well-modeled by exponential distributions — the majority of orders arrive on time (near zero delay) and there is a diminishing probability of increasingly large delays. This matches real-world freight and pharma supply data.

### A.5 The sawtooth inventory simulation

```python
stock = item.max_capacity
snapshots = []
for day in range(90):
    month = (start_date + timedelta(days=day)).month
    season = get_season(month)
    dow = (start_date + timedelta(days=day)).weekday()
    consumption = (
        item.daily_consumption_normal
        × SEASONAL_MULTIPLIER[item.disaster_surge_category][season]
        × DAY_OF_WEEK_MULTIPLIER[dow]
    )
    stock = max(0, stock - consumption)
    if stock <= item.reorder_level:
        restock_qty = random.randint(
            item.reorder_level * 2,
            item.max_capacity
        )
        stock = min(stock + restock_qty, item.max_capacity)
    snapshots.append((item.item_id, start_date + timedelta(days=day), round(stock, 1)))

# current_stock = snapshots[-1][2]
```

This produces realistic inventory curves that show the characteristic sawtooth pattern of real hospital stores management, which any evaluator with supply chain knowledge will recognize as credible.

### A.6 Purchase Order value generation

```python
UNIT_PRICE_INR = {
    "medicine":    {"low": 2, "high": 500},      # e.g. Paracetamol ₹2/tab, Insulin ₹450/vial
    "consumable":  {"low": 5, "high": 150},       # e.g. Glove ₹5, IV cannula ₹80
    "instrument":  {"low": 200, "high": 15000},   # e.g. Scalpel ₹200, Retractor ₹12000
    "equipment":   {"low": 2000, "high": 150000}, # e.g. BP monitor ₹3000, Infusion pump ₹80000
}

unit_price = random.uniform(
    UNIT_PRICE_INR[item.category]["low"],
    UNIT_PRICE_INR[item.category]["high"]
)
po.total_value_inr = round(order.quantity × unit_price, 2)
```

This ensures PO values are in realistic INR ranges that a hospital finance department would recognize.
