# Hospital Supply Chain — Presentation & PPT Guide

This document provides a structured breakdown of the project, organized into "Slides" or sections to help you build a professional PowerPoint presentation.

---

## Slide 1: Title Slide
*   **Project Name:** Hospital Supply Chain: AI-Powered Delivery & Disaster Prediction System
*   **Tagline:** Protecting Life-Critical Supplies with Real-Time Intelligence.
*   **Focus:** Bridging the gap between normal operations and emergency response.

---

## Slide 2: The Problem (Pain Points)
*   **Normal Mode Failures:** Deliveries get delayed without warning, leading to stock-outs of life-critical items (e.g., Insulin, Morphine).
*   **Disaster Mode Failures:** Natural or man-made disasters (floods, earthquakes) surge demand unpredictably, block supply routes, and isolate suppliers.
*   **Lack of Visibility:** Hospitals often lack real-time data on *where* their supplies are and *when* they will actually arrive during a crisis.

---

## Slide 3: The Solution (Overview)
*   **Predictive Analytics:** Uses local AI (Ollama) to predict delivery delays *before* they happen.
*   **Disaster Intelligence:** Automatically monitors global alerts (GDACS, ReliefWeb) to detect regional crises.
*   **Automated Response:** During a disaster, the system automatically:
    *   Calculates demand surge multipliers.
    *   Identifies blocked supply routes.
    *   Recommends emergency suppliers outside the impact zone.

---

## Slide 4: Key Features — Normal Mode
*   **Live Dashboard:** Real-time tracking of orders, inventory, and supplier reliability.
*   **AI Delay Prediction:** Uses Qwen2.5 (Local LLM) to analyze supplier history, season, and criticality to estimate revised ETAs.
*   **Procurement Workflow:** Integrated Purchase Orders (PO) and Goods Receipt Notes (GRN) for end-to-end supply tracking.

---

## Slide 5: Key Features — Disaster Mode
*   **Disaster Trigger:** System switches to a "Red Alert" dashboard when a disaster is detected within range.
*   **Surge Prediction:** Predicts 3x–5x demand spikes for trauma and respiratory supplies based on disaster type.
*   **Alternate Routing:** Integrates OpenRouteService (ORS) to find the fastest routes avoiding "Impact Zones."
*   **Emergency Suppliers:** Highlights "Emergency Certified" suppliers that can operate during crises.

---

## Slide 6: Technical Stack
*   **Frontend:** React 18, Vite, Tailwind CSS, Leaflet.js (Maps).
*   **Backend:** FastAPI (Python 3.11), SQLAlchemy, APScheduler (Background polling).
*   **AI Module:** Ollama (Local LLM - No cloud costs, 100% data privacy).
*   **External APIs:** NewsAPI (News), GDACS (Natural disasters), ReliefWeb (UN Reports), OpenRouteService (Routing).
*   **Database:** SQLite (Demo) / PostgreSQL (Production).

---

## Slide 7: System Architecture
*   **Data Ingestion:** Periodic polling of GDACS and NewsAPI.
*   **AI Processing:** Raw text is sent to Ollama for severity analysis and surge prediction.
*   **Dynamic UI:** React dashboard polls the backend for an `active_disaster` flag to switch modes instantly.

---

## Slide 8: Data Strategy (Synthetic Excellence)
*   **Realistic Distributions:** Not just random data.
    *   **Bimodal Reliability:** Simulates "Good" vs "Poor" suppliers.
    *   **Sawtooth Inventory:** Mimics real-world consumption and restock cycles.
    *   **Exponential Delays:** Realistic delay patterns correlated to Monsoon seasons and supplier distance.
*   **Scalability:** Designed to handle 10,000+ orders and 500+ item categories.

---

## Slide 9: Business Value & Impact
*   **Risk Mitigation:** Reduce stock-out risks for life-critical items by 40% through early warnings.
*   **Cost Efficiency:** Avoid emergency shipping premiums by identifying delays 48-72 hours in advance.
*   **Operational Resilience:** Centralized "Command Center" for hospital administrators during state-level emergencies.

---

## Slide 10: Conclusion & Future Roadmap
*   **Current Status:** Fully functional POC with AI-driven dashboard and disaster simulation.
*   **Next Steps:**
    *   Integration with Hospital ERP systems.
    *   Multi-hospital "Cluster" support for resource sharing.
    *   IoT integration for real-time truck tracking.
