# Hospital Supply Chain — Data Specification

This document outlines the exact dataset columns, recommended volumes, and statistical distributions required to build a "demo-ready" state-of-the-art Hospital Supply Chain system.

---

## 1. Recommended Data Volume
To ensure the dashboard looks premium and the AI/Disaster simulations feel robust, the following volumes are recommended:

| Table | Current | **Recommended (Ideal)** | Why? |
| :--- | :--- | :--- | :--- |
| **Suppliers** | 30 | **150+** | Enables a dense map visualization and provides multiple alternate options per category. |
| **Items** | 80 | **500+** | Simulates a full-scale hospital pharmacy and surgical store inventory. |
| **Orders** | 500 | **10,000+** | Provides enough history for meaningful trend analysis and AI delay prediction training. |
| **Inventory** | 80 | **500+** | Maps 1:1 with items. Shows a "full" stock status board with multiple stock-out alerts. |
| **Disaster History**| 50 | **200+** | Gives the AI (Ollama) significant context to predict surge multipliers for new events. |
| **Delivery History**| 500 | **10,000+** | Necessary to establish supplier reliability benchmarks (Normal vs Monsoon vs Disaster). |

---

## 2. Table Schemas & Column Details

### 2.1 Suppliers (`suppliers`)
*The backbone for logistics and map-based disaster response.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `supplier_id` | UUID | Primary Key |
| `name` | String | Company Name |
| `city`, `state` | String | Regional location |
| `lat`, `lng` | Float | **Critical:** Geocoordinates for disaster radius and routing logic. |
| `reliability_score` | Float | 0.0–1.0. Historical on-time delivery rate. |
| `avg_lead_days` | Integer | Base delivery time in days. |
| `supply_categories` | JSON | Array: `["medicine", "surgical", "consumable", "equipment"]` |
| `is_emergency_certified`| Bool | True if the supplier is vetted for disaster-mode operations. |
| `is_govt_reserve` | Bool | Flag for central/state medical stores (CMSS, etc). |

### 2.2 Items & Inventory (`items`, `inventory`)
*Defines the critical medical supplies being managed.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `item_id` | UUID | Primary Key |
| `name`, `category` | String | e.g., "Paracetamol", "N95 Mask" |
| `criticality` | Enum | `life_critical`, `high`, `medium`, `low` |
| `current_stock` | Integer | Current units in the hospital. |
| `reorder_level` | Integer | Threshold that triggers a restock order. |
| `max_capacity` | Integer | Warehouse storage limit. |
| `daily_consumption_normal` | Float | Average units consumed per day during normal operations. |
| `daily_consumption_disaster`| Float | **Critical:** Surge consumption rate (e.g., 3.5x normal). |
| `disaster_surge_category` | String | `trauma`, `respiratory`, `burn`, `general` (used for AI clustering). |

### 2.3 Orders & Delivery History (`orders`, `delivery_history`)
*Transactional data for trend analysis and delay prediction.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `order_id` | UUID | Primary Key |
| `item_id`, `supplier_id` | UUID | Foreign Keys |
| `quantity` | Integer | Total units ordered. |
| `order_date` | DateTime | When the order was placed. |
| `expected_delivery_date` | Date | The promised arrival date. |
| `status` | Enum | `pending`, `in_transit`, `delivered`, `delayed`, `cancelled` |
| `delay_days` | Integer | Actual arrival date - Expected arrival date. |
| `delay_reason` | Enum | `weather`, `transport`, `stock_out`, `disaster`, `customs` |

### 2.4 Disaster Intelligence (`disaster_events`, `disaster_predictions`)
*Data required for the "Disaster Mode" simulation.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `event_id` | UUID | Primary Key |
| `disaster_type` | Enum | `flood`, `earthquake`, `cyclone`, `fire`, `collapse` |
| `severity` | Integer | 1 (Minor) to 5 (Catastrophic) |
| `lat`, `lng`, `radius_km` | Float | **Disaster Zone:** Defines which suppliers and routes are impacted. |
| `ai_summary` | Text | Ollama-generated summary of the incident. |
| `surge_multiplier` | Float | Predicted increase in demand for specific items (e.g., 4.2x). |
| `predicted_stockout_hours`| Float | How long current stock will last under surge demand. |

---

## 3. Data Generation Strategy

To make the data realistic, the following distributions are applied:
1.  **Reliability (Bimodal):** 70% of suppliers are "Reliable" (mean=0.9), 30% are "Unreliable" (mean=0.6).
2.  **Lead Time (Distance-based):** `1 + (distance / 300)` + noise. Closer suppliers are naturally faster.
3.  **Consumption (Sawtooth):** Inventory follows a "Sawtooth" pattern where stock drops daily and jumps up on restocks.
4.  **Delays (Exponential):** Delays aren't random; they follow an exponential decay, with higher probability during "Monsoon" season or for low-reliability suppliers.

---

## 4. Why This Matters
*   **Predictive Power:** With 10,000 orders, the AI can reliably say: *"Supplier X has a 40% chance of a 3-day delay during the Monsoon for Life Critical items."*
*   **Visual Impact:** 150+ suppliers ensure the map doesn't look empty and that "Alternate Routes" actually have multiple starting points.
*   **Business Logic:** High-criticality items with low stock and high surge multipliers are prioritized at the top of the "Action Required" list.
